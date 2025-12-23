# System Architecture

## Overview

The Enterprise Sales Analytics & Visualization System follows a layered architecture pattern, separating concerns across data storage, processing, analytics, and presentation layers.

## Architecture Layers

### 1. Data Layer (Oracle Database)

**Purpose**: Persistent storage of transactional and analytical data

**Components**:
- **Reference Tables**: REGIONS, CUSTOMERS, PRODUCTS
- **Transaction Table**: SALES_TRANSACTIONS (fact table)
- **Analytics Tables**: KPI_RESULTS
- **Logging Tables**: DATA_VALIDATION_LOG, ERROR_LOG

**Key Features**:
- Normalized schema design
- Foreign key relationships
- Check constraints for data integrity
- Indexes for query performance
- Sequences for primary key generation

### 2. Processing Layer (PL/SQL)

**Purpose**: Business logic execution at database level

**Components**:
- **PKG_ERROR_LOGGING**: Centralized error handling
- **PKG_DATA_VALIDATION**: Data quality checks
- **PKG_KPI_CALCULATIONS**: KPI computation procedures

**Key Features**:
- Stored procedures for reusable logic
- Exception handling and error logging
- Transaction management
- Cursor-based data retrieval

### 3. Analytics Layer (Python)

**Purpose**: Data processing, analysis, and insight generation

**Components**:
- **Data Loader**: CSV/Excel ingestion
- **Data Validator**: Validation orchestration
- **KPI Calculator**: KPI computation coordination
- **Insight Generator**: Rule-based analytics

**Key Features**:
- Pandas for data manipulation
- Database connectivity via cx_Oracle
- Statistical analysis
- Anomaly detection algorithms

### 4. Visualization Layer (Python)

**Purpose**: Report and chart generation

**Components**:
- **Chart Generator**: Multiple visualization formats
- **Report Generator**: Text and CSV outputs

**Key Features**:
- Static charts (Matplotlib, Seaborn)
- Interactive dashboards (Plotly)
- Multiple output formats
- Automated report generation

### 5. Automation Layer (Unix Shell)

**Purpose**: Pipeline orchestration and scheduling

**Components**:
- **run_pipeline.sh**: Main execution script
- **validate_data.sh**: Validation wrapper
- **generate_reports.sh**: Report generation wrapper
- **setup_cron.sh**: Cron job configuration

**Key Features**:
- Error handling and logging
- Environment validation
- Cron scheduling support
- Exit code management

## Data Flow

```
CSV File → Python Loader → Oracle DB → PL/SQL Validation
                                              ↓
                                    PL/SQL KPI Calculation
                                              ↓
                                    Python Analytics → Insights
                                              ↓
                                    Python Visualization → Reports
```

## Technology Stack

- **Database**: Oracle 11g+
- **Backend**: Python 3.8+
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Automation**: Bash Shell Scripts, Cron
- **Configuration**: YAML

## Scalability Considerations

- Indexed database tables for fast queries
- Batch insert operations for data loading
- Efficient PL/SQL procedures
- Modular Python architecture
- Configurable thresholds and parameters

## Security Considerations

- Database credentials in config file (not committed)
- Input validation at multiple layers
- Error logging without exposing sensitive data
- File archiving for audit trail

