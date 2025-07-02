from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import json
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetwise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(7), nullable=False)  # Format: YYYY-MM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False)
    split_months = db.Column(db.Integer, default=1)  # Number of months to split expense
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavingGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'budget_warning', 'goal_achieved', 'monthly_summary'
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM format

class RecurringExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # 'monthly', 'weekly', 'yearly'
    day_of_month = db.Column(db.Integer, nullable=True)  # For monthly expenses
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_processed = db.Column(db.DateTime, nullable=True)

class BudgetTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    income_amount = db.Column(db.Float, nullable=False)
    needs_percentage = db.Column(db.Float, default=50.0)
    wants_percentage = db.Column(db.Float, default=30.0)
    savings_percentage = db.Column(db.Float, default=20.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_default = db.Column(db.Boolean, default=False)

# Forms
class IncomeForm(FlaskForm):
    amount = FloatField('Monthly Income (£)', validators=[DataRequired(), NumberRange(min=0)])
    month = StringField('Month (YYYY-MM)', validators=[DataRequired()])
    submit = SubmitField('Add Income')

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount (£)', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('needs', 'Needs'),
        ('wants', 'Wants'),
        ('savings', 'Savings')
    ], validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    split_months = SelectField('Split Over Months', choices=[
        (1, '1 month'),
        (2, '2 months'),
        (3, '3 months'),
        (6, '6 months'),
        (12, '12 months')
    ], coerce=int, default=1)
    submit = SubmitField('Add Expense')

class SavingGoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired()])
    target_amount = FloatField('Target Amount (£)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Create Goal')

class AddToGoalForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Add to Goal')

class RecurringExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Category', choices=[
        ('needs', 'Needs'),
        ('wants', 'Wants'),
        ('savings', 'Savings')
    ], validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly')
    ], validators=[DataRequired()])
    day_of_month = StringField('Day of Month (1-31, leave empty for other frequencies)')
    submit = SubmitField('Add Recurring Expense')

class BudgetTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired()])
    description = StringField('Description (optional)')
    income_amount = FloatField('Monthly Income', validators=[DataRequired(), NumberRange(min=0.01)])
    needs_percentage = FloatField('Needs Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
    wants_percentage = FloatField('Wants Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
    savings_percentage = FloatField('Savings Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Save Template')

# Helper functions
def get_current_month():
    return datetime.now().strftime('%Y-%m')

def get_previous_month(month):
    """Get the previous month in YYYY-MM format"""
    current_date = datetime.strptime(month, '%Y-%m')
    previous_date = current_date - relativedelta(months=1)
    return previous_date.strftime('%Y-%m')

def get_next_month(month):
    """Get the next month in YYYY-MM format"""
    current_date = datetime.strptime(month, '%Y-%m')
    next_date = current_date + relativedelta(months=1)
    return next_date.strftime('%Y-%m')

def get_month_budget(income_amount):
    return {
        'needs': income_amount * 0.5,
        'wants': income_amount * 0.3,
        'savings': income_amount * 0.2
    }

def get_month_expenses(month, category=None):
    query = Expense.query.filter(
        db.func.strftime('%Y-%m', Expense.date) == month
    )
    if category:
        query = query.filter(Expense.category == category)
    return query.all()

def calculate_split_expense(expense):
    """Calculate the monthly amount for split expenses"""
    if expense.split_months > 1:
        return expense.amount / expense.split_months
    return expense.amount

def get_remaining_budget(month):
    """Get remaining budget for the month"""
    income = Income.query.filter_by(month=month).first()
    if not income:
        return {'needs': 0, 'wants': 0, 'savings': 0}
    
    budget = get_month_budget(income.amount)
    expenses = get_month_expenses(month)
    
    spent = {'needs': 0, 'wants': 0, 'savings': 0}
    
    for expense in expenses:
        monthly_amount = calculate_split_expense(expense)
        spent[expense.category] += monthly_amount
    
    remaining = {}
    for category in budget:
        remaining[category] = budget[category] - spent[category]
    
    return remaining

def handle_wants_overflow(month):
    """Handle wants budget overflow by deducting from next month"""
    remaining = get_remaining_budget(month)
    if remaining['wants'] < 0:
        # Get next month
        current_date = datetime.strptime(month, '%Y-%m')
        next_month = (current_date + relativedelta(months=1)).strftime('%Y-%m')
        
        # Check if next month income exists
        next_income = Income.query.filter_by(month=next_month).first()
        if next_income:
            # Reduce next month's wants budget
            next_budget = get_month_budget(next_income.amount)
            overflow_amount = abs(remaining['wants'])
            
            # Create a virtual expense for next month to track the overflow
            overflow_expense = Expense(
                amount=overflow_amount,
                category='wants',
                description=f'Overflow from {month}',
                date=datetime.strptime(f"{next_month}-01", '%Y-%m-%d').date(),
                split_months=1
            )
            db.session.add(overflow_expense)
            db.session.commit()

def check_budget_alerts(month):
    """Check budget thresholds and create alerts"""
    income = Income.query.filter_by(month=month).first()
    if not income:
        return []
    
    budget = get_month_budget(income.amount)
    expenses = get_month_expenses(month)
    
    alerts = []
    
    # Calculate totals by category
    totals = {'needs': 0, 'wants': 0, 'savings': 0}
    for expense in expenses:
        monthly_amount = calculate_split_expense(expense)
        totals[expense.category] += monthly_amount
    
    # Check budget warnings (80% threshold)
    for category, spent in totals.items():
        budget_limit = budget[category]
        percentage = (spent / budget_limit) * 100 if budget_limit > 0 else 0
        
        if percentage >= 80 and percentage < 100:
            # Check if alert already exists
            existing_alert = Notification.query.filter_by(
                type='budget_warning',
                month=month,
                title=f'{category.title()} Budget Warning'
            ).first()
            
            if not existing_alert:
                alert = Notification(
                    type='budget_warning',
                    title=f'{category.title()} Budget Warning',
                    message=f'You have used {percentage:.1f}% of your {category} budget (£{spent:.2f} of £{budget_limit:.2f})',
                    month=month
                )
                db.session.add(alert)
                alerts.append(alert)
        
        elif percentage >= 100:
            # Check if alert already exists
            existing_alert = Notification.query.filter_by(
                type='budget_warning',
                month=month,
                title=f'{category.title()} Budget Exceeded'
            ).first()
            
            if not existing_alert:
                alert = Notification(
                    type='budget_warning',
                    title=f'{category.title()} Budget Exceeded',
                    message=f'You have exceeded your {category} budget by £{spent - budget_limit:.2f}',
                    month=month
                )
                db.session.add(alert)
                alerts.append(alert)
    
    # Check goal achievements
    goals = SavingGoal.query.all()
    for goal in goals:
        if goal.current_amount >= goal.target_amount:
            # Check if achievement notification already exists
            existing_notification = Notification.query.filter_by(
                type='goal_achieved',
                title=f'Goal Achieved: {goal.name}'
            ).first()
            
            if not existing_notification:
                notification = Notification(
                    type='goal_achieved',
                    title=f'Goal Achieved: {goal.name}',
                    message=f'Congratulations! You have reached your goal of £{goal.target_amount:.2f} for {goal.name}',
                    month=month
                )
                db.session.add(notification)
                alerts.append(notification)
    
    if alerts:
        db.session.commit()
    
    return alerts

# Routes
@app.route('/')
@app.route('/<month>')
def dashboard(month=None):
    if month is None:
        current_month = get_current_month()
    else:
        current_month = month
    
    income = Income.query.filter_by(month=current_month).first()
    
    if not income:
        return render_template('dashboard.html', 
                             income=None, 
                             budget=None, 
                             expenses=[], 
                             remaining=None,
                             totals={'needs': 0, 'wants': 0, 'savings': 0},
                             saving_goals=[],
                             current_month=current_month,
                             previous_month=get_previous_month(current_month),
                             next_month=get_next_month(current_month),
                             alerts=[],
                             notifications=[])
    
    budget = get_month_budget(income.amount)
    # --- Search & Filter ---
    expenses_query = Expense.query.filter(
        db.func.strftime('%Y-%m', Expense.date) == current_month
    )
    search = request.args.get('search', '').strip()
    if search:
        expenses_query = expenses_query.filter(Expense.description.ilike(f'%{search}%'))
    category = request.args.get('category', '').strip()
    if category:
        expenses_query = expenses_query.filter_by(category=category)
    start_date = request.args.get('start_date', '').strip()
    if start_date:
        expenses_query = expenses_query.filter(Expense.date >= start_date)
    end_date = request.args.get('end_date', '').strip()
    if end_date:
        expenses_query = expenses_query.filter(Expense.date <= end_date)
    min_amount = request.args.get('min_amount', '').strip()
    if min_amount:
        expenses_query = expenses_query.filter(Expense.amount >= float(min_amount))
    max_amount = request.args.get('max_amount', '').strip()
    if max_amount:
        expenses_query = expenses_query.filter(Expense.amount <= float(max_amount))
    expenses = expenses_query.order_by(Expense.date.desc()).all()
    # --- End Search & Filter ---
    remaining = get_remaining_budget(current_month)
    saving_goals = SavingGoal.query.all()
    
    # Calculate totals by category
    totals = {'needs': 0, 'wants': 0, 'savings': 0}
    for expense in expenses:
        monthly_amount = calculate_split_expense(expense)
        totals[expense.category] += monthly_amount
    
    # Check for budget alerts
    alerts = check_budget_alerts(current_month)
    notifications = Notification.query.filter_by(is_read=False).order_by(Notification.created_at.desc()).all()
    
    return render_template('dashboard.html',
                         income=income,
                         budget=budget,
                         expenses=expenses,
                         remaining=remaining,
                         totals=totals,
                         saving_goals=saving_goals,
                         current_month=current_month,
                         previous_month=get_previous_month(current_month),
                         next_month=get_next_month(current_month),
                         alerts=alerts,
                         notifications=notifications)

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    form = IncomeForm()
    if form.validate_on_submit():
        # Check if income for this month already exists
        existing_income = Income.query.filter_by(month=form.month.data).first()
        if existing_income:
            existing_income.amount = form.amount.data
        else:
            new_income = Income(amount=form.amount.data, month=form.month.data)
            db.session.add(new_income)
        
        db.session.commit()
        flash('Income added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_income.html', form=form)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        new_expense = Expense(
            amount=form.amount.data,
            category=form.category.data,
            description=form.description.data,
            date=form.date.data,
            split_months=form.split_months.data
        )
        db.session.add(new_expense)
        db.session.commit()
        
        # Handle wants overflow
        month = form.date.data.strftime('%Y-%m')
        handle_wants_overflow(month)
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_expense.html', form=form)

@app.route('/add_saving_goal', methods=['GET', 'POST'])
def add_saving_goal():
    form = SavingGoalForm()
    if form.validate_on_submit():
        new_goal = SavingGoal(
            name=form.name.data,
            target_amount=form.target_amount.data
        )
        db.session.add(new_goal)
        db.session.commit()
        flash('Saving goal created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_saving_goal.html', form=form)

@app.route('/save_remaining/<category>', methods=['GET', 'POST'])
def save_remaining(category):
    current_month = get_current_month()
    remaining = get_remaining_budget(current_month)
    
    if request.method == 'GET':
        # Show allocation form
        goals = SavingGoal.query.all()
        if not goals:
            flash('No saving goals found. Please create a saving goal first.', 'warning')
            return redirect(url_for('dashboard'))
        
        if remaining[category] <= 0:
            flash(f'No remaining budget in {category} category.', 'warning')
            return redirect(url_for('dashboard'))
        
        return render_template('allocate_savings.html', 
                             category=category, 
                             remaining_amount=remaining[category],
                             goals=goals,
                             current_month=current_month)
    
    else:  # POST request
        if remaining[category] > 0:
            # Get allocation data from form
            total_allocated = 0
            goals = SavingGoal.query.all()
            
            for goal in goals:
                amount_key = f'amount_{goal.id}'
                if amount_key in request.form:
                    try:
                        amount = float(request.form[amount_key])
                        if amount > 0:
                            goal.current_amount += amount
                            total_allocated += amount
                    except ValueError:
                        continue
            
            if total_allocated > 0:
                db.session.commit()
                flash(f'£{total_allocated:.2f} allocated to saving goals from {category} remaining budget!', 'success')
            else:
                flash('No amounts were allocated. Please enter valid amounts.', 'warning')
        else:
            flash(f'No remaining budget in {category} category.', 'warning')
        
        return redirect(url_for('dashboard'))

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_saving_goal/<int:id>')
def delete_saving_goal(id):
    goal = SavingGoal.query.get_or_404(id)
    db.session.delete(goal)
    db.session.commit()
    flash('Saving goal deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_to_goal/<int:goal_id>', methods=['GET', 'POST'])
def add_to_goal(goal_id):
    goal = SavingGoal.query.get_or_404(goal_id)
    
    if request.method == 'GET':
        return render_template('add_to_goal.html', goal=goal)
    
    else:  # POST request
        try:
            amount = float(request.form.get('amount', 0))
            if amount > 0:
                goal.current_amount += amount
                db.session.commit()
                flash(f'£{amount:.2f} added to "{goal.name}" goal!', 'success')
            else:
                flash('Please enter a valid amount greater than 0.', 'warning')
        except ValueError:
            flash('Please enter a valid amount.', 'warning')
        
        return redirect(url_for('dashboard'))

@app.route('/mark_notification_read/<int:notification_id>')
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/notifications')
def view_notifications():
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/clear_all_notifications')
def clear_all_notifications():
    Notification.query.update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/recurring_expenses')
def view_recurring_expenses():
    recurring_expenses = RecurringExpense.query.filter_by(is_active=True).all()
    return render_template('recurring_expenses.html', recurring_expenses=recurring_expenses)

@app.route('/add_recurring_expense', methods=['GET', 'POST'])
def add_recurring_expense():
    form = RecurringExpenseForm()
    if form.validate_on_submit():
        recurring_expense = RecurringExpense(
            description=form.description.data,
            amount=form.amount.data,
            category=form.category.data,
            frequency=form.frequency.data,
            day_of_month=form.day_of_month.data if form.day_of_month.data else None
        )
        db.session.add(recurring_expense)
        db.session.commit()
        flash('Recurring expense added successfully!', 'success')
        return redirect(url_for('view_recurring_expenses'))
    return render_template('add_recurring_expense.html', form=form)

@app.route('/toggle_recurring_expense/<int:expense_id>')
def toggle_recurring_expense(expense_id):
    recurring_expense = RecurringExpense.query.get_or_404(expense_id)
    recurring_expense.is_active = not recurring_expense.is_active
    db.session.commit()
    status = 'activated' if recurring_expense.is_active else 'deactivated'
    flash(f'Recurring expense {status}!', 'success')
    return redirect(url_for('view_recurring_expenses'))

@app.route('/delete_recurring_expense/<int:expense_id>')
def delete_recurring_expense(expense_id):
    recurring_expense = RecurringExpense.query.get_or_404(expense_id)
    db.session.delete(recurring_expense)
    db.session.commit()
    flash('Recurring expense deleted successfully!', 'success')
    return redirect(url_for('view_recurring_expenses'))

@app.route('/budget_templates')
def view_budget_templates():
    templates = BudgetTemplate.query.order_by(BudgetTemplate.created_at.desc()).all()
    return render_template('budget_templates.html', templates=templates)

@app.route('/add_budget_template', methods=['GET', 'POST'])
def add_budget_template():
    form = BudgetTemplateForm()
    if form.validate_on_submit():
        # Validate that percentages sum to 100
        total_percentage = form.needs_percentage.data + form.wants_percentage.data + form.savings_percentage.data
        if abs(total_percentage - 100) > 0.01:
            flash('Percentages must sum to 100%', 'error')
            return render_template('add_budget_template.html', form=form)
        
        template = BudgetTemplate(
            name=form.name.data,
            description=form.description.data,
            income_amount=form.income_amount.data,
            needs_percentage=form.needs_percentage.data,
            wants_percentage=form.wants_percentage.data,
            savings_percentage=form.savings_percentage.data
        )
        db.session.add(template)
        db.session.commit()
        flash('Budget template saved successfully!', 'success')
        return redirect(url_for('view_budget_templates'))
    return render_template('add_budget_template.html', form=form)

@app.route('/apply_budget_template/<int:template_id>')
def apply_budget_template(template_id):
    template = BudgetTemplate.query.get_or_404(template_id)
    current_month = get_current_month()
    
    # Check if income already exists for this month
    existing_income = Income.query.filter_by(month=current_month).first()
    if existing_income:
        flash(f'Income already exists for {current_month}. Please delete it first to apply a template.', 'warning')
        return redirect(url_for('view_budget_templates'))
    
    # Create income using template
    income = Income(
        amount=template.income_amount,
        month=current_month
    )
    db.session.add(income)
    db.session.commit()
    
    flash(f'Budget template "{template.name}" applied successfully for {current_month}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_budget_template/<int:template_id>')
def delete_budget_template(template_id):
    template = BudgetTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    flash('Budget template deleted successfully!', 'success')
    return redirect(url_for('view_budget_templates'))

@app.route('/export_monthly_report', methods=['GET'])
def export_monthly_report():
    current_month = get_current_month()
    income = Income.query.filter_by(month=current_month).first()
    
    if not income:
        flash('No income data found for the current month.', 'warning')
        return redirect(url_for('dashboard'))
    
    budget = get_month_budget(income.amount)
    expenses = get_month_expenses(current_month)
    remaining = get_remaining_budget(current_month)
    saving_goals = SavingGoal.query.all()
    
    # Calculate totals by category
    totals = {'needs': 0, 'wants': 0, 'savings': 0}
    for expense in expenses:
        monthly_amount = calculate_split_expense(expense)
        totals[expense.category] += monthly_amount
    
    # Generate CSV content
    csv_content = io.StringIO()
    csv_writer = csv.writer(csv_content)
    
    # Write header
    csv_writer.writerow(['Category', 'Budget', 'Expenses', 'Remaining'])
    
    # Write data
    for category, budget_amount in budget.items():
        csv_writer.writerow([category.title(), budget_amount, totals[category], remaining[category]])
    
    # Write totals
    csv_writer.writerow(['Total', sum(budget.values()), sum(totals.values()), sum(remaining.values())])
    
    # Write saving goals
    for goal in saving_goals:
        csv_writer.writerow([goal.name, goal.target_amount, goal.current_amount, goal.target_amount - goal.current_amount])
    
    # Get CSV content
    csv_content.seek(0)
    csv_data = csv_content.read()
    
    # Create response
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = f'attachment; filename=monthly_report_{current_month}.csv'
    response.mimetype = 'text/csv'
    
    return response

@app.route('/bulk_expense_action/<month>', methods=['POST'])
def bulk_expense_action(month):
    ids = request.form.getlist('expense_ids')
    action = request.form.get('action')
    if not ids:
        flash('No expenses selected.', 'warning')
        return redirect(url_for('dashboard', month=month))
    if action == 'delete':
        for eid in ids:
            expense = Expense.query.get(eid)
            if expense:
                db.session.delete(expense)
        db.session.commit()
        flash(f'Deleted {len(ids)} expenses.', 'success')
    elif action == 'change_category':
        new_category = request.form.get('new_category')
        if not new_category:
            flash('No category selected.', 'warning')
            return redirect(url_for('dashboard', month=month))
        for eid in ids:
            expense = Expense.query.get(eid)
            if expense:
                expense.category = new_category
        db.session.commit()
        flash(f'Changed category for {len(ids)} expenses.', 'success')
    return redirect(url_for('dashboard', month=month))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        

    
    app.run(debug=True) 