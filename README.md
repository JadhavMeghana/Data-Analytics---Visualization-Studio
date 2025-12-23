# Enterprise Sales Analytics & Visualization System

## 📋 Business Problem

This system addresses the need for automated, enterprise-grade sales data analytics in an IT services environment. It processes large volumes of sales transaction data, validates data quality, calculates key performance indicators (KPIs), and generates automated reports and visualizations.

**Key Business Challenges Solved:**
- Manual data analysis is time-consuming and error-prone
- Lack of real-time insights into sales performance
- Inconsistent KPI calculations across teams
- No automated anomaly detection
- Limited visibility into regional and customer performance

## 🏗️ Architecture

```
┌─────────────┐
│  CSV/Excel  │
│   Files     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│  Python Loader   │─────▶│   Oracle     │
│  (Data Ingestion)│      │  Database    │
└─────────────────┘      └──────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  PL/SQL Procedures     │
                    │  - Data Validation     │
                    │  - KPI Calculations    │
                    │  - Error Logging       │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Python Analytics     │
                    │  - Insight Generation │
                    │  - Chart Creation     │
                    │  - Report Generation  │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Reports & Charts      │
                    │  - PNG Charts         │
                    │  - HTML Dashboards   │
                    │  - CSV Summaries     │
                    │  - Text Reports      │
                    └──────────────────────┘
```

## 🛠️ Tech Stack

- **Database**: Oracle SQL + PL/SQL (Procedures, Packages)
- **Backend**: Python 3.8+
  - pandas: Data manipulation
  - cx_Oracle: Oracle database connectivity
  - matplotlib/seaborn/plotly: Visualization
  - PyYAML: Configuration management
- **Automation**: Unix Shell Scripting + Cron
- **Optional UI**: Flask (for simple web interface)

## 📊 KPIs Delivered

1. **Revenue by Region**: Total sales revenue segmented by geographic region
2. **Monthly Revenue Trend**: Time-series analysis of revenue over months
3. **Top Customers**: Identification of highest-value customers
4. **Product Performance**: Revenue analysis by product
5. **Average Transaction Value**: Mean value of individual transactions

## 🤖 Automation Achieved

- **Daily Data Processing**: Automated CSV/Excel file ingestion
- **Data Validation**: Automated quality checks and error logging
- **KPI Calculation**: Scheduled computation of all KPIs
- **Report Generation**: Automated creation of charts and summaries
- **Anomaly Detection**: Rule-based outlier identification
- **Trend Analysis**: Automated trend detection and insights

## 📁 Project Structure

```
enterprise-sales-analytics/
├── database/          # Oracle SQL/PL/SQL scripts
├── python/            # Python analytics modules
├── scripts/           # Unix shell scripts
├── data/              # Input/archive data files
├── reports/           # Generated reports and charts
├── logs/              # Application logs
└── config.yaml        # Configuration file
```

## 🚀 How to Run Locally

### Prerequisites

1. **Oracle Database** (Oracle Express Edition or higher)
   - Create user: `SALES_ANALYTICS`
   - Grant necessary privileges

2. **Python 3.8+** with pip

3. **Unix-like environment** (Linux/Mac/WSL for Windows)

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd enterprise-sales-analytics
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   - Copy `config.yaml.example` to `config.yaml`
   - Update database credentials in `config.yaml`

5. **Set up Oracle database**
   ```bash
   sqlplus SALES_ANALYTICS/password@localhost:1521/XE @database/scripts/install_all.sql
   ```

6. **Prepare your data (or use sample links below)**
   - Place your CSV/XLSX files in `data/input/` if using the pipeline scripts
   - For the Streamlit app, just upload the files directly (multiple files supported)
   - Optional legacy sales schema for pipeline: transaction_date, customer_id, product_id, quantity, unit_price, total_amount, region_id

### Running the Pipeline

**Option 1: Run with CSV file**
```bash
./scripts/run_pipeline.sh data/input/sales_data.csv
```

**Option 2: Run without data load (KPI calculation only)**
```bash
./scripts/run_pipeline.sh
```

**Option 3: Run individual components**
```bash
# Validate data
./scripts/validate_data.sh

# Generate reports
./scripts/generate_reports.sh
```

**Option 4: Run Python directly**
```bash
python python/main.py data/input/sales_data.csv
```

### Streamlit Analytics Studio (dynamic schema, your own data)

```bash
# Activate venv
.\venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate      # macOS/Linux

# Install streamlit if needed
pip install streamlit

# Run Streamlit app
streamlit run python/streamlit_app.py --server.maxUploadSize=500
```

Features:
- Upload your own CSV/XLSX (multiple files supported); no bundled sample fallback
- Dynamic column mapping (pick date, numeric, and category columns)
- Generic KPIs and visuals; sales-specific charts appear only if classic sales columns exist
- Outlier detection (requires a chosen date + numeric column)
- Dataset narrative summary and data preview

### Sample datasets for testing (XLSX)
- Product Sales by Region: https://excelx.com/wp-content/uploads/2025/06/Product-Sales-Region.xlsx
- Online Store Orders: https://excelx.com/wp-content/uploads/2025/06/Online-Store-Orders.xlsx
- Retail Store Transactions: https://excelx.com/wp-content/uploads/2025/06/Retail-Store-Transactions.xlsx

### Setting Up Cron Job

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Setup cron (runs daily at 2 AM)
./scripts/setup_cron.sh
# Follow instructions to add cron job
```

## 📈 Sample CSV Format

```csv
transaction_date,customer_id,product_id,quantity,unit_price,total_amount,region_id
2024-01-15,1,101,10,50.00,500.00,1
2024-01-16,2,102,5,100.00,500.00,2
2024-01-17,1,103,20,25.00,500.00,1
```

## 📝 Output Files

- **Charts**: `reports/charts/`
  - `revenue_by_region.png`
  - `monthly_revenue_trend.png`
  - `top_customers.png`
  - `interactive_dashboard.html`

- **Reports**: `reports/summaries/`
  - `kpi_summary_YYYYMMDD.csv`
  - `report_YYYYMMDD_HHMMSS.txt`

- **Insights**: `reports/insights/`
  - `insights_YYYYMMDD_HHMMSS.txt`

- **Logs**: `logs/`
  - `app.log`
  - `error.log`
  - `pipeline_YYYYMMDD_HHMMSS.log`

## 🔍 Key Features

- ✅ **Data Validation**: Comprehensive checks for data quality
- ✅ **Error Handling**: Robust error logging and recovery
- ✅ **Performance**: Indexed database tables for fast queries
- ✅ **Scalability**: Handles large datasets efficiently
- ✅ **Automation**: Fully automated pipeline execution
- ✅ **Visualization**: Multiple chart types (static and interactive)
- ✅ **Insights**: Rule-based anomaly and trend detection

## 👨‍💼 Interview-Ready Features

This project demonstrates:
- Enterprise database design (normalized schema, indexes, constraints)
- PL/SQL programming (packages, procedures, error handling)
- Python data engineering (pandas, database connectivity)
- Unix shell scripting and automation
- Data validation and quality assurance
- KPI calculation and business intelligence
- Visualization and reporting
- Production-ready code structure

## 📞 Support

For issues or questions, check the logs in `logs/` directory.

## 📄 License

This project is created for educational and interview preparation purposes.

