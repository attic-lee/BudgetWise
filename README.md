# BudgetWise - Personal Finance Manager

A modern, web-based personal finance application that implements the **50/30/20 budgeting rule** to help you manage your money effectively and achieve your financial goals.

## 🎯 Features

### Core Budgeting (50/30/20 Rule)
- **50% for Needs**: Essential expenses like housing, utilities, groceries, and transportation
- **30% for Wants**: Discretionary spending like dining out, entertainment, hobbies, and shopping
- **20% for Savings**: Emergency fund, investments, and debt repayment

### Smart Expense Tracking
- **Category-based expenses** with automatic budget allocation
- **Multi-month expense splitting** (e.g., shampoo that lasts 3 months)
- **Real-time budget tracking** with visual progress bars
- **Expense history** with detailed breakdowns

### Quick Add System
- **Editable quick expense templates** for frequently used items
- **Pre-configured items**: Transportation (Oyster), Hobby (Tennis)
- **Instant expense addition** with customizable amounts

### Saving Goals
- **Multiple saving goals** with progress tracking
- **Automatic savings allocation** from remaining budget
- **50% of remaining budget** automatically saved to goals
- **Visual progress indicators** for each goal

### Smart Budget Management
- **Wants overflow handling**: Excess spending deducted from next month
- **British Pounds (£) currency** throughout the application
- **Monthly budget reset** with income tracking
- **Real-time remaining budget calculations**

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd BudgetWise
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Start managing your finances!

## 📱 Usage Guide

### Getting Started

1. **Add Monthly Income**
   - Click "Add Income" on the dashboard
   - Enter your monthly income amount
   - Specify the month (YYYY-MM format)
   - The app will automatically calculate your 50/30/20 budget

2. **Add Expenses**
   - Click "Add Expense" to add detailed expenses
   - Choose category (Needs/Wants/Savings)
   - Add description and date
   - Use "Split Over Months" for long-lasting items

3. **Use Quick Add**
   - Edit amounts for pre-configured items (Oyster, Tennis)
   - Click "Add" to instantly add to your budget
   - Create new quick add templates as needed

### Managing Your Budget

#### Budget Overview
- **Visual progress bars** show spending vs. budget
- **Remaining amounts** displayed for each category
- **Color-coded indicators**: Green (under budget), Red (over budget)

#### Saving Goals
- **Create multiple goals** (Emergency Fund, Vacation, etc.)
- **Automatic savings** from remaining budget
- **Progress tracking** with percentage completion

#### Expense Management
- **View all expenses** with category breakdown
- **Delete expenses** if needed
- **Split expense tracking** shows monthly allocations

### Advanced Features

#### Multi-Month Expense Splitting
- Perfect for items that last multiple months
- Examples: shampoo (3 months), annual subscriptions (12 months)
- Automatically distributes cost across selected months

#### Wants Overflow Protection
- If you exceed your wants budget, the excess is deducted from next month
- Helps maintain long-term budget discipline
- Automatic tracking of overflow amounts

#### Smart Savings
- 50% of remaining budget automatically saved to goals
- Distributes savings equally among all active goals
- Helps build wealth while maintaining budget discipline

## 🎨 User Interface

### Modern Design
- **Responsive layout** works on desktop and mobile
- **Beautiful gradients** and smooth animations
- **Intuitive navigation** with clear call-to-action buttons
- **Real-time updates** without page refreshes

### Visual Elements
- **Progress bars** for budget categories
- **Color-coded categories**: Red (Needs), Orange (Wants), Green (Savings)
- **Interactive elements** with hover effects
- **Flash messages** for user feedback

## 🔧 Technical Details

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Font Awesome icons
- **Forms**: Flask-WTF with validation

### Database Models
- **Income**: Monthly income tracking
- **Expense**: Expense records with categories and splitting
- **SavingGoal**: Financial goals with progress tracking
- **QuickAdd**: Template expenses for quick access

### Key Functions
- **Budget calculation** based on 50/30/20 rule
- **Expense splitting** across multiple months
- **Overflow handling** for wants category
- **Automatic savings** allocation

## 📊 Example Usage

### Scenario: Monthly Income of £3,000

**Budget Allocation:**
- Needs (50%): £1,500
- Wants (30%): £900
- Savings (20%): £600

**Example Expenses:**
- Rent: £1,200 (Needs)
- Groceries: £200 (Needs)
- Netflix: £15 (Wants)
- Tennis lessons: £50 (Wants)
- Emergency fund: £300 (Savings)

**Quick Add Items:**
- Oyster Card: £150 (Transportation)
- Tennis equipment: £80 (Hobby)

### Multi-Month Splitting Example
- Annual gym membership: £360
- Split over 12 months: £30/month
- Automatically tracked across the year

## 🛠️ Customization

### Adding New Quick Add Items
1. Go to "Add Quick Expense"
2. Enter category and description
3. Set default amount
4. Use from dashboard

### Creating Saving Goals
1. Click "Add Saving Goal"
2. Name your goal (e.g., "Emergency Fund")
3. Set target amount
4. Track progress automatically

### Modifying Budget Categories
The 50/30/20 rule is hardcoded but can be modified in the `get_month_budget()` function in `app.py`.

## 🔒 Data Security

- **Local database** stores all data on your machine
- **No external data sharing** or cloud storage
- **Simple backup**: Copy the `budgetwise.db` file

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'flask'"**
   - Run: `pip install -r requirements.txt`

2. **Database errors**
   - Delete `budgetwise.db` and restart the app
   - Database will be recreated automatically

3. **Port already in use**
   - Change port in `app.py` line: `app.run(debug=True, port=5001)`

### Support
- Check that all dependencies are installed
- Ensure Python 3.7+ is being used
- Verify database file permissions

## 📈 Future Enhancements

Potential features for future versions:
- **Export functionality** (CSV, PDF reports)
- **Multiple currencies** support
- **Recurring expenses** automation
- **Budget alerts** and notifications
- **Mobile app** version
- **Data visualization** charts and graphs

## 📄 License

This project is open source and available under the MIT License.

---

**Start your journey to financial freedom with BudgetWise!** 🎉 