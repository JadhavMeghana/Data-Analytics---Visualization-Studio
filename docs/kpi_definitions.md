# KPI Definitions and Calculations

## Overview

This document defines all Key Performance Indicators (KPIs) calculated by the system, including their formulas, business logic, and calculation methods.

## KPI List

### 1. Revenue by Region

**KPI Name**: `REVENUE_BY_REGION`

**Description**: Total sales revenue aggregated by geographic region and date

**Formula**:
```
Revenue by Region = SUM(TOTAL_AMOUNT) 
                   WHERE TRANSACTION_DATE BETWEEN start_date AND end_date
                   GROUP BY REGION_ID, TRANSACTION_DATE
```

**Calculation Method**:
- Aggregates sales transactions by region and date
- Includes all transactions with valid region_id
- Stored with daily granularity

**Usage**: Regional performance analysis, geographic distribution

**PL/SQL Procedure**: `PKG_KPI_CALCULATIONS.CALC_REVENUE_BY_REGION`

---

### 2. Monthly Revenue Trend

**KPI Name**: `MONTHLY_REVENUE_TREND`

**Description**: Total revenue aggregated by month for trend analysis

**Formula**:
```
Monthly Revenue = SUM(TOTAL_AMOUNT)
                  WHERE TRANSACTION_DATE BETWEEN start_date AND end_date
                  GROUP BY TRUNC(TRANSACTION_DATE, 'MM')
```

**Calculation Method**:
- Aggregates all transactions by month
- Uses Oracle TRUNC function to group by month
- Provides time-series data for trend analysis

**Usage**: Revenue trend analysis, month-over-month comparison

**PL/SQL Procedure**: `PKG_KPI_CALCULATIONS.CALC_MONTHLY_REVENUE_TREND`

---

### 3. Top Customers

**KPI Name**: `TOP_CUSTOMERS`

**Description**: Revenue ranking of top N customers

**Formula**:
```
Top Customers = SELECT CUSTOMER_ID, SUM(TOTAL_AMOUNT) as REVENUE
                WHERE TRANSACTION_DATE BETWEEN start_date AND end_date
                GROUP BY CUSTOMER_ID
                ORDER BY REVENUE DESC
                LIMIT top_n
```

**Calculation Method**:
- Aggregates revenue by customer
- Ranks customers by total revenue
- Returns top N customers (default: 10)
- Uses ROW_NUMBER() window function for ranking

**Usage**: Customer segmentation, account management, sales targeting

**PL/SQL Procedure**: `PKG_KPI_CALCULATIONS.CALC_TOP_CUSTOMERS`

**Parameters**:
- `p_top_n`: Number of top customers to return (default: 10)

---

### 4. Product Performance

**KPI Name**: `PRODUCT_PERFORMANCE`

**Description**: Revenue aggregated by product and date

**Formula**:
```
Product Performance = SUM(TOTAL_AMOUNT)
                      WHERE TRANSACTION_DATE BETWEEN start_date AND end_date
                      GROUP BY PRODUCT_ID, TRANSACTION_DATE
```

**Calculation Method**:
- Aggregates sales by product and date
- Provides daily product-level revenue
- Enables product-level analysis

**Usage**: Product performance analysis, inventory planning

**PL/SQL Procedure**: `PKG_KPI_CALCULATIONS.CALC_PRODUCT_PERFORMANCE`

---

### 5. Average Transaction Value

**KPI Name**: `AVG_TRANSACTION_VALUE`

**Description**: Mean value of individual transactions

**Formula**:
```
Average Transaction Value = AVG(TOTAL_AMOUNT)
                            WHERE TRANSACTION_DATE BETWEEN start_date AND end_date
                            GROUP BY TRANSACTION_DATE
```

**Calculation Method**:
- Calculates daily average transaction value
- Uses Oracle AVG() aggregate function
- Provides insight into transaction size trends

**Usage**: Transaction size analysis, pricing strategy

**PL/SQL Procedure**: `PKG_KPI_CALCULATIONS.CALC_AVG_TRANSACTION_VALUE`

---

## KPI Storage

All KPIs are stored in the `KPI_RESULTS` table with the following structure:

- **KPI_NAME**: Identifier for the KPI
- **KPI_VALUE**: Calculated value
- **KPI_DATE**: Date for which KPI is calculated
- **REGION_ID**: Optional region filter (NULL for global KPIs)
- **CALCULATION_DATE**: Timestamp when KPI was calculated

## Calculation Frequency

- **Default**: Last 30 days from current date
- **Configurable**: Start and end dates can be specified
- **Automated**: Daily via cron job
- **On-Demand**: Can be triggered manually

## Data Refresh Strategy

- **Incremental**: New calculations append to existing data
- **Date Range**: Previous calculations for same date range are deleted before recalculation
- **Idempotent**: Can be run multiple times safely

## Performance Considerations

- Indexes on KPI_NAME and KPI_DATE for fast retrieval
- Batch processing for large date ranges
- Efficient aggregation using Oracle SQL
- Cursor-based retrieval for Python consumption

## Usage Examples

### Retrieve Revenue by Region
```sql
SELECT r.REGION_NAME, k.KPI_VALUE
FROM KPI_RESULTS k
JOIN REGIONS r ON k.REGION_ID = r.REGION_ID
WHERE k.KPI_NAME = 'REVENUE_BY_REGION'
AND k.KPI_DATE >= SYSDATE - 30
ORDER BY k.KPI_VALUE DESC;
```

### Get Monthly Trend
```sql
SELECT KPI_DATE, KPI_VALUE
FROM KPI_RESULTS
WHERE KPI_NAME = 'MONTHLY_REVENUE_TREND'
ORDER BY KPI_DATE;
```

### Top Customers
```sql
SELECT c.CUSTOMER_NAME, k.KPI_VALUE as REVENUE
FROM KPI_RESULTS k
JOIN CUSTOMERS c ON k.KPI_VALUE = (
    SELECT SUM(TOTAL_AMOUNT)
    FROM SALES_TRANSACTIONS
    WHERE CUSTOMER_ID = c.CUSTOMER_ID
)
WHERE k.KPI_NAME = 'TOP_CUSTOMERS'
ORDER BY k.KPI_VALUE DESC;
```

## Business Rules

1. **Revenue Calculation**: Includes all transactions regardless of discount
2. **Date Filtering**: Uses transaction date, not load date
3. **NULL Handling**: NULL region_id excluded from regional KPIs
4. **Rounding**: Values stored with 2 decimal places
5. **Time Zones**: All dates use database server timezone

