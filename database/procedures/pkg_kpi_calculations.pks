-- =====================================================
-- KPI Calculations Package Specification
-- =====================================================

CREATE OR REPLACE PACKAGE PKG_KPI_CALCULATIONS AS
    
    -- Calculate Total Revenue by Region
    PROCEDURE CALC_REVENUE_BY_REGION(
        p_start_date IN DATE,
        p_end_date IN DATE
    );
    
    -- Calculate Monthly Revenue Trend
    PROCEDURE CALC_MONTHLY_REVENUE_TREND(
        p_start_date IN DATE,
        p_end_date IN DATE
    );
    
    -- Calculate Top N Customers
    PROCEDURE CALC_TOP_CUSTOMERS(
        p_start_date IN DATE,
        p_end_date IN DATE,
        p_top_n IN NUMBER DEFAULT 10
    );
    
    -- Calculate Product Performance
    PROCEDURE CALC_PRODUCT_PERFORMANCE(
        p_start_date IN DATE,
        p_end_date IN DATE
    );
    
    -- Calculate Average Transaction Value
    PROCEDURE CALC_AVG_TRANSACTION_VALUE(
        p_start_date IN DATE,
        p_end_date IN DATE
    );
    
    -- Get KPI Results as Cursor (for Python consumption)
    FUNCTION GET_KPI_RESULTS(
        p_kpi_name IN VARCHAR2,
        p_start_date IN DATE DEFAULT NULL,
        p_end_date IN DATE DEFAULT NULL
    ) RETURN SYS_REFCURSOR;
    
END PKG_KPI_CALCULATIONS;
/

