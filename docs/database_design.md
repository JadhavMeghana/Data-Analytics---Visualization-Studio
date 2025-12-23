# Database Design Documentation

## Entity Relationship Diagram

```
REGIONS (1) ────< (M) CUSTOMERS
   │                      │
   │                      │
   │                      │
   │                  SALES_TRANSACTIONS
   │                      │
   │                      │
   │                      │
   └──────────────────────┘
                        │
                        │
                   PRODUCTS (1)
```

## Table Descriptions

### REGIONS
**Purpose**: Geographic region master data

**Columns**:
- REGION_ID (PK): Unique identifier
- REGION_NAME: Name of region
- REGION_CODE: Short code (unique)
- COUNTRY: Country name
- CREATED_DATE: Record creation timestamp

**Constraints**:
- Primary key on REGION_ID
- Unique constraint on REGION_CODE
- Check constraint: REGION_ID > 0

### CUSTOMERS
**Purpose**: Customer master data

**Columns**:
- CUSTOMER_ID (PK): Unique identifier
- CUSTOMER_NAME: Customer name
- CUSTOMER_CODE: Unique customer code
- REGION_ID (FK): Reference to REGIONS
- CUSTOMER_TYPE: Type of customer
- CREATED_DATE: Record creation timestamp

**Constraints**:
- Primary key on CUSTOMER_ID
- Foreign key to REGIONS
- Unique constraint on CUSTOMER_CODE
- Check constraint: CUSTOMER_ID > 0

### PRODUCTS
**Purpose**: Product master data

**Columns**:
- PRODUCT_ID (PK): Unique identifier
- PRODUCT_NAME: Product name
- PRODUCT_CODE: Unique product code
- CATEGORY: Product category
- UNIT_PRICE: Standard unit price
- CREATED_DATE: Record creation timestamp

**Constraints**:
- Primary key on PRODUCT_ID
- Unique constraint on PRODUCT_CODE
- Check constraints: PRODUCT_ID > 0, UNIT_PRICE >= 0

### SALES_TRANSACTIONS
**Purpose**: Sales transaction fact table

**Columns**:
- TRANSACTION_ID (PK): Unique identifier
- TRANSACTION_DATE: Date of transaction
- CUSTOMER_ID (FK): Reference to CUSTOMERS
- PRODUCT_ID (FK): Reference to PRODUCTS
- QUANTITY: Quantity sold
- UNIT_PRICE: Price per unit
- TOTAL_AMOUNT: Total transaction amount
- REGION_ID (FK): Reference to REGIONS
- DISCOUNT_PERCENTAGE: Discount applied
- LOAD_DATE: Data load timestamp

**Constraints**:
- Primary key on TRANSACTION_ID
- Foreign keys to CUSTOMERS, PRODUCTS, REGIONS
- Check constraints:
  - TRANSACTION_ID > 0
  - QUANTITY > 0
  - UNIT_PRICE > 0
  - TOTAL_AMOUNT >= 0
  - DISCOUNT_PERCENTAGE between 0 and 100

### KPI_RESULTS
**Purpose**: Calculated KPI values storage

**Columns**:
- KPI_ID (PK): Unique identifier
- KPI_NAME: Name of KPI
- KPI_VALUE: Calculated value
- KPI_DATE: Date for which KPI is calculated
- REGION_ID (FK): Optional region filter
- CALCULATION_DATE: When KPI was calculated

**Constraints**:
- Primary key on KPI_ID
- Foreign key to REGIONS (optional)

### DATA_VALIDATION_LOG
**Purpose**: Data validation audit trail

**Columns**:
- VALIDATION_ID (PK): Unique identifier
- VALIDATION_DATE: When validation ran
- TABLE_NAME: Table validated
- VALIDATION_TYPE: Type of validation
- RECORDS_CHECKED: Total records checked
- RECORDS_PASSED: Records that passed
- RECORDS_FAILED: Records that failed
- VALIDATION_STATUS: PASS/FAIL/WARNING
- ERROR_DETAILS: Detailed error information

**Constraints**:
- Check constraint: VALIDATION_STATUS in ('PASS', 'FAIL', 'WARNING')

### ERROR_LOG
**Purpose**: Centralized error logging

**Columns**:
- ERROR_ID (PK): Unique identifier
- ERROR_DATE: When error occurred
- ERROR_SOURCE: Source of error
- ERROR_TYPE: Type of error
- ERROR_MESSAGE: Error message
- ERROR_STACK: Stack trace
- RESOLUTION_STATUS: PENDING/RESOLVED/IGNORED

**Constraints**:
- Check constraint: RESOLUTION_STATUS in ('PENDING', 'RESOLVED', 'IGNORED')

## Indexes

### SALES_TRANSACTIONS Indexes
- IDX_SALES_TRANS_DATE: On TRANSACTION_DATE
- IDX_SALES_CUSTOMER: On CUSTOMER_ID
- IDX_SALES_PRODUCT: On PRODUCT_ID
- IDX_SALES_REGION: On REGION_ID
- IDX_SALES_DATE_REGION: Composite on (TRANSACTION_DATE, REGION_ID)
- IDX_SALES_DATE_CUSTOMER: Composite on (TRANSACTION_DATE, CUSTOMER_ID)

### KPI_RESULTS Indexes
- IDX_KPI_NAME_DATE: Composite on (KPI_NAME, KPI_DATE)
- IDX_KPI_REGION: On REGION_ID
- IDX_KPI_DATE: On KPI_DATE

### Other Indexes
- IDX_CUSTOMER_REGION: On CUSTOMERS.REGION_ID
- IDX_CUSTOMER_CODE: On CUSTOMERS.CUSTOMER_CODE
- Indexes on log tables for date and status fields

## Sequences

- SEQ_REGION_ID: For REGIONS table
- SEQ_CUSTOMER_ID: For CUSTOMERS table
- SEQ_PRODUCT_ID: For PRODUCTS table
- SEQ_TRANSACTION_ID: For SALES_TRANSACTIONS table
- SEQ_KPI_ID: For KPI_RESULTS table
- SEQ_VALIDATION_ID: For DATA_VALIDATION_LOG table
- SEQ_ERROR_ID: For ERROR_LOG table

## Normalization

The database follows 3NF (Third Normal Form):
- No transitive dependencies
- Each non-key attribute depends only on the primary key
- Reference data separated into master tables
- Fact table contains only foreign keys and measures

## Data Integrity

- Foreign key constraints ensure referential integrity
- Check constraints enforce business rules
- NOT NULL constraints on critical fields
- Unique constraints prevent duplicates
- Validation procedures check data quality

