-- =====================================================
-- KPI Calculations Package Body
-- =====================================================

CREATE OR REPLACE PACKAGE BODY PKG_KPI_CALCULATIONS AS
    
    PROCEDURE CALC_REVENUE_BY_REGION(
        p_start_date IN DATE,
        p_end_date IN DATE
    ) IS
    BEGIN
        -- Delete existing results for this KPI
        DELETE FROM KPI_RESULTS
        WHERE KPI_NAME = 'REVENUE_BY_REGION'
        AND KPI_DATE BETWEEN p_start_date AND p_end_date;
        
        -- Calculate and insert revenue by region
        INSERT INTO KPI_RESULTS (
            KPI_ID,
            KPI_NAME,
            KPI_VALUE,
            KPI_DATE,
            REGION_ID,
            CALCULATION_DATE
        )
        SELECT 
            SEQ_KPI_ID.NEXTVAL,
            'REVENUE_BY_REGION',
            SUM(TOTAL_AMOUNT),
            TRUNC(s.TRANSACTION_DATE),
            s.REGION_ID,
            SYSDATE
        FROM SALES_TRANSACTIONS s
        WHERE s.TRANSACTION_DATE BETWEEN p_start_date AND p_end_date
        AND s.REGION_ID IS NOT NULL
        GROUP BY TRUNC(s.TRANSACTION_DATE), s.REGION_ID;
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_KPI_CALCULATIONS.CALC_REVENUE_BY_REGION',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            ROLLBACK;
            RAISE;
    END CALC_REVENUE_BY_REGION;
    
    PROCEDURE CALC_MONTHLY_REVENUE_TREND(
        p_start_date IN DATE,
        p_end_date IN DATE
    ) IS
    BEGIN
        DELETE FROM KPI_RESULTS
        WHERE KPI_NAME = 'MONTHLY_REVENUE_TREND'
        AND KPI_DATE BETWEEN TRUNC(p_start_date, 'MM') AND TRUNC(p_end_date, 'MM');
        
        INSERT INTO KPI_RESULTS (
            KPI_ID,
            KPI_NAME,
            KPI_VALUE,
            KPI_DATE,
            REGION_ID,
            CALCULATION_DATE
        )
        SELECT 
            SEQ_KPI_ID.NEXTVAL,
            'MONTHLY_REVENUE_TREND',
            SUM(TOTAL_AMOUNT),
            TRUNC(TRANSACTION_DATE, 'MM'),
            NULL,
            SYSDATE
        FROM SALES_TRANSACTIONS
        WHERE TRANSACTION_DATE BETWEEN p_start_date AND p_end_date
        GROUP BY TRUNC(TRANSACTION_DATE, 'MM');
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_KPI_CALCULATIONS.CALC_MONTHLY_REVENUE_TREND',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            ROLLBACK;
            RAISE;
    END CALC_MONTHLY_REVENUE_TREND;
    
    PROCEDURE CALC_TOP_CUSTOMERS(
        p_start_date IN DATE,
        p_end_date IN DATE,
        p_top_n IN NUMBER DEFAULT 10
    ) IS
    BEGIN
        DELETE FROM KPI_RESULTS
        WHERE KPI_NAME = 'TOP_CUSTOMERS'
        AND KPI_DATE BETWEEN p_start_date AND p_end_date;
        
        INSERT INTO KPI_RESULTS (
            KPI_ID,
            KPI_NAME,
            KPI_VALUE,
            KPI_DATE,
            REGION_ID,
            CALCULATION_DATE
        )
        SELECT 
            SEQ_KPI_ID.NEXTVAL,
            'TOP_CUSTOMERS',
            total_revenue,
            p_end_date,
            NULL,
            SYSDATE
        FROM (
            SELECT 
                s.CUSTOMER_ID,
                SUM(s.TOTAL_AMOUNT) AS total_revenue,
                ROW_NUMBER() OVER (ORDER BY SUM(s.TOTAL_AMOUNT) DESC) AS rn
            FROM SALES_TRANSACTIONS s
            WHERE s.TRANSACTION_DATE BETWEEN p_start_date AND p_end_date
            GROUP BY s.CUSTOMER_ID
            ORDER BY total_revenue DESC
        )
        WHERE rn <= p_top_n;
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_KPI_CALCULATIONS.CALC_TOP_CUSTOMERS',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            ROLLBACK;
            RAISE;
    END CALC_TOP_CUSTOMERS;
    
    PROCEDURE CALC_PRODUCT_PERFORMANCE(
        p_start_date IN DATE,
        p_end_date IN DATE
    ) IS
    BEGIN
        DELETE FROM KPI_RESULTS
        WHERE KPI_NAME = 'PRODUCT_PERFORMANCE'
        AND KPI_DATE BETWEEN p_start_date AND p_end_date;
        
        INSERT INTO KPI_RESULTS (
            KPI_ID,
            KPI_NAME,
            KPI_VALUE,
            KPI_DATE,
            REGION_ID,
            CALCULATION_DATE
        )
        SELECT 
            SEQ_KPI_ID.NEXTVAL,
            'PRODUCT_PERFORMANCE',
            SUM(TOTAL_AMOUNT),
            TRUNC(TRANSACTION_DATE),
            NULL,
            SYSDATE
        FROM SALES_TRANSACTIONS
        WHERE TRANSACTION_DATE BETWEEN p_start_date AND p_end_date
        GROUP BY PRODUCT_ID, TRUNC(TRANSACTION_DATE);
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_KPI_CALCULATIONS.CALC_PRODUCT_PERFORMANCE',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            ROLLBACK;
            RAISE;
    END CALC_PRODUCT_PERFORMANCE;
    
    PROCEDURE CALC_AVG_TRANSACTION_VALUE(
        p_start_date IN DATE,
        p_end_date IN DATE
    ) IS
    BEGIN
        DELETE FROM KPI_RESULTS
        WHERE KPI_NAME = 'AVG_TRANSACTION_VALUE'
        AND KPI_DATE BETWEEN p_start_date AND p_end_date;
        
        INSERT INTO KPI_RESULTS (
            KPI_ID,
            KPI_NAME,
            KPI_VALUE,
            KPI_DATE,
            REGION_ID,
            CALCULATION_DATE
        )
        SELECT 
            SEQ_KPI_ID.NEXTVAL,
            'AVG_TRANSACTION_VALUE',
            AVG(TOTAL_AMOUNT),
            TRUNC(TRANSACTION_DATE),
            NULL,
            SYSDATE
        FROM SALES_TRANSACTIONS
        WHERE TRANSACTION_DATE BETWEEN p_start_date AND p_end_date
        GROUP BY TRUNC(TRANSACTION_DATE);
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_KPI_CALCULATIONS.CALC_AVG_TRANSACTION_VALUE',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            ROLLBACK;
            RAISE;
    END CALC_AVG_TRANSACTION_VALUE;
    
    FUNCTION GET_KPI_RESULTS(
        p_kpi_name IN VARCHAR2,
        p_start_date IN DATE DEFAULT NULL,
        p_end_date IN DATE DEFAULT NULL
    ) RETURN SYS_REFCURSOR IS
        v_cursor SYS_REFCURSOR;
    BEGIN
        IF p_start_date IS NULL AND p_end_date IS NULL THEN
            OPEN v_cursor FOR
                SELECT KPI_ID, KPI_NAME, KPI_VALUE, KPI_DATE, REGION_ID, CALCULATION_DATE
                FROM KPI_RESULTS
                WHERE KPI_NAME = p_kpi_name
                ORDER BY KPI_DATE DESC;
        ELSE
            OPEN v_cursor FOR
                SELECT KPI_ID, KPI_NAME, KPI_VALUE, KPI_DATE, REGION_ID, CALCULATION_DATE
                FROM KPI_RESULTS
                WHERE KPI_NAME = p_kpi_name
                AND KPI_DATE BETWEEN NVL(p_start_date, KPI_DATE) AND NVL(p_end_date, KPI_DATE)
                ORDER BY KPI_DATE DESC;
        END IF;
        
        RETURN v_cursor;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_KPI_CALCULATIONS.GET_KPI_RESULTS',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            RAISE;
    END GET_KPI_RESULTS;
    
END PKG_KPI_CALCULATIONS;
/

