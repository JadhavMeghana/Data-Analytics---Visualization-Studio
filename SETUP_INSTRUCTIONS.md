# Setup Instructions

## ✅ Completed Steps

1. ✅ Project structure created
2. ✅ Configuration file created (`config.yaml` - **UPDATE DATABASE CREDENTIALS**)
3. ✅ Python virtual environment created
4. ✅ Python dependencies installed

## ⚠️ Next Steps Required

### 1. Update Database Configuration

Edit `config.yaml` and update the following:
- `database.host`: Your Oracle database host
- `database.port`: Your Oracle database port (default: 1521)
- `database.service_name`: Your Oracle service name (e.g., XE, ORCL)
- `database.username`: Your Oracle username
- `database.password`: Your Oracle password (**CHANGE THIS!**)

### 2. Set Up Oracle Database

#### Create Database User (if not exists)

Connect to Oracle as SYSDBA and run:

```sql
CREATE USER SALES_ANALYTICS IDENTIFIED BY your_password;
GRANT CONNECT, RESOURCE, CREATE VIEW, CREATE PROCEDURE TO SALES_ANALYTICS;
GRANT UNLIMITED TABLESPACE TO SALES_ANALYTICS;
```

#### Install Database Schema

```bash
sqlplus SALES_ANALYTICS/password@localhost:1521/XE @database/scripts/install_all.sql
```

Or using SQL Developer:
1. Open SQL Developer
2. Connect as SALES_ANALYTICS user
3. Open `database/scripts/install_all.sql`
4. Run the script

### 3. Test the Installation

#### Option A: Test with Sample Data

```bash
# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Run pipeline with sample CSV
python python/main.py data/input/sales_data_sample.csv
```

#### Option B: Test Individual Components

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Test data validation
python -c "from python.analytics.data_validator import DataValidator; v = DataValidator(); print(v.validate_all())"

# Test KPI calculation
python -c "from python.analytics.kpi_calculator import KPICalculator; k = KPICalculator(); k.calculate_all_kpis()"

# Generate reports
python -c "from python.visualization.chart_generator import ChartGenerator; c = ChartGenerator(); c.generate_all_charts()"
```

### 4. Prepare Your Data

Place your CSV files in `data/input/` directory with the following format:

```csv
transaction_date,customer_id,product_id,quantity,unit_price,total_amount,region_id,discount_percentage
2024-01-15,1,101,10,50.00,500.00,1,0
```

**Required Columns:**
- `transaction_date`: Date in YYYY-MM-DD format
- `customer_id`: Integer customer ID (must exist in CUSTOMERS table)
- `product_id`: Integer product ID (must exist in PRODUCTS table)
- `quantity`: Numeric quantity
- `unit_price`: Numeric unit price
- `total_amount`: Numeric total amount

**Optional Columns:**
- `region_id`: Integer region ID (must exist in REGIONS table)
- `discount_percentage`: Numeric discount percentage (0-100)

### 5. Set Up Master Data

Before loading transactions, ensure you have:

1. **Regions** - Already loaded via `04_initial_data.sql`
2. **Customers** - Insert customer records:
   ```sql
   INSERT INTO CUSTOMERS (CUSTOMER_ID, CUSTOMER_NAME, CUSTOMER_CODE, REGION_ID)
   VALUES (SEQ_CUSTOMER_ID.NEXTVAL, 'Customer Name', 'CUST001', 1);
   ```
3. **Products** - Insert product records:
   ```sql
   INSERT INTO PRODUCTS (PRODUCT_ID, PRODUCT_NAME, PRODUCT_CODE, CATEGORY, UNIT_PRICE)
   VALUES (SEQ_PRODUCT_ID.NEXTVAL, 'Product Name', 'PROD001', 'Category', 50.00);
   ```

## 🔧 Troubleshooting

### Oracle Connection Issues

1. **Check Oracle Instant Client**: Ensure Oracle Instant Client is installed and in PATH
2. **Test Connection**: 
   ```bash
   python -c "from python.data_loader.oracle_connector import OracleConnector; OracleConnector().connect()"
   ```
3. **Check TNS Names**: Verify service name is correct in `config.yaml`

### Import Errors

If you get import errors:
```bash
# Ensure you're in the project root directory
cd "c:\Boring Project"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify Python path includes project root
python -c "import sys; print(sys.path)"
```

### Database Schema Issues

If schema installation fails:
1. Check user permissions
2. Verify tablespace availability
3. Review error logs in Oracle alert log
4. Try running scripts individually:
   ```bash
   sqlplus SALES_ANALYTICS/password@localhost:1521/XE @database/schema/01_create_tables.sql
   ```

## 📝 Notes

- The virtual environment is located at `venv/`
- Configuration file is at `config.yaml` (not committed to git)
- Logs are written to `logs/` directory
- Reports are generated in `reports/` directory
- Sample data is in `data/input/sales_data_sample.csv`

## 🚀 Quick Start

Once database is set up:

```bash
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Load sample data
python python/main.py data/input/sales_data_sample.csv

# 3. Check reports
# - Charts: reports/charts/
# - Summaries: reports/summaries/
# - Insights: reports/insights/
```

