-- =====================================================
-- Data Validation Package Body
-- =====================================================

CREATE OR REPLACE PACKAGE BODY PKG_DATA_VALIDATION AS
    
    PROCEDURE VALIDATE_SALES_DATA(
        p_validation_date IN DATE DEFAULT SYSDATE,
        p_result OUT VARCHAR2,
        p_records_checked OUT NUMBER,
        p_records_passed OUT NUMBER,
        p_records_failed OUT NUMBER
    ) IS
        v_failed_count NUMBER := 0;
        v_passed_count NUMBER := 0;
        v_total_count NUMBER := 0;
        v_error_details CLOB := '';
    BEGIN
        -- Count total records
        SELECT COUNT(*) INTO v_total_count
        FROM SALES_TRANSACTIONS
        WHERE TRUNC(LOAD_DATE) = TRUNC(p_validation_date);
        
        -- Check for NULL values in critical fields
        SELECT COUNT(*) INTO v_failed_count
        FROM SALES_TRANSACTIONS
        WHERE TRUNC(LOAD_DATE) = TRUNC(p_validation_date)
        AND (TRANSACTION_DATE IS NULL
             OR CUSTOMER_ID IS NULL
             OR PRODUCT_ID IS NULL
             OR QUANTITY IS NULL
             OR UNIT_PRICE IS NULL
             OR TOTAL_AMOUNT IS NULL);
        
        IF v_failed_count > 0 THEN
            v_error_details := v_error_details || 'Found ' || v_failed_count || ' records with NULL values. ';
        END IF;
        
        -- Check for negative amounts
        SELECT COUNT(*) INTO v_failed_count
        FROM SALES_TRANSACTIONS
        WHERE TRUNC(LOAD_DATE) = TRUNC(p_validation_date)
        AND (QUANTITY <= 0 OR UNIT_PRICE <= 0 OR TOTAL_AMOUNT < 0);
        
        IF v_failed_count > 0 THEN
            v_error_details := v_error_details || 'Found ' || v_failed_count || ' records with invalid amounts. ';
        END IF;
        
        -- Check for future dates
        SELECT COUNT(*) INTO v_failed_count
        FROM SALES_TRANSACTIONS
        WHERE TRUNC(LOAD_DATE) = TRUNC(p_validation_date)
        AND TRANSACTION_DATE > SYSDATE;
        
        IF v_failed_count > 0 THEN
            v_error_details := v_error_details || 'Found ' || v_failed_count || ' records with future dates. ';
        END IF;
        
        v_passed_count := v_total_count - v_failed_count;
        
        -- Determine result
        IF v_failed_count = 0 THEN
            p_result := 'PASS';
        ELSIF v_failed_count < v_total_count * 0.1 THEN
            p_result := 'WARNING';
        ELSE
            p_result := 'FAIL';
        END IF;
        
        p_records_checked := v_total_count;
        p_records_passed := v_passed_count;
        p_records_failed := v_failed_count;
        
        -- Log validation result
        INSERT INTO DATA_VALIDATION_LOG (
            VALIDATION_ID,
            VALIDATION_DATE,
            TABLE_NAME,
            VALIDATION_TYPE,
            RECORDS_CHECKED,
            RECORDS_PASSED,
            RECORDS_FAILED,
            VALIDATION_STATUS,
            ERROR_DETAILS
        ) VALUES (
            SEQ_VALIDATION_ID.NEXTVAL,
            SYSDATE,
            'SALES_TRANSACTIONS',
            'DATA_QUALITY',
            v_total_count,
            v_passed_count,
            v_failed_count,
            p_result,
            v_error_details
        );
        
        COMMIT;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_DATA_VALIDATION.VALIDATE_SALES_DATA',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            p_result := 'FAIL';
            p_records_checked := 0;
            p_records_passed := 0;
            p_records_failed := 0;
            RAISE;
    END VALIDATE_SALES_DATA;
    
    PROCEDURE VALIDATE_REFERENTIAL_INTEGRITY(
        p_result OUT VARCHAR2,
        p_error_details OUT CLOB
    ) IS
        v_invalid_customer NUMBER := 0;
        v_invalid_product NUMBER := 0;
        v_invalid_region NUMBER := 0;
    BEGIN
        -- Check for invalid customer references
        SELECT COUNT(*) INTO v_invalid_customer
        FROM SALES_TRANSACTIONS s
        WHERE NOT EXISTS (SELECT 1 FROM CUSTOMERS c WHERE c.CUSTOMER_ID = s.CUSTOMER_ID);
        
        -- Check for invalid product references
        SELECT COUNT(*) INTO v_invalid_product
        FROM SALES_TRANSACTIONS s
        WHERE NOT EXISTS (SELECT 1 FROM PRODUCTS p WHERE p.PRODUCT_ID = s.PRODUCT_ID);
        
        -- Check for invalid region references
        SELECT COUNT(*) INTO v_invalid_region
        FROM SALES_TRANSACTIONS s
        WHERE s.REGION_ID IS NOT NULL
        AND NOT EXISTS (SELECT 1 FROM REGIONS r WHERE r.REGION_ID = s.REGION_ID);
        
        p_error_details := 'Invalid Customers: ' || v_invalid_customer || 
                          '; Invalid Products: ' || v_invalid_product ||
                          '; Invalid Regions: ' || v_invalid_region;
        
        IF v_invalid_customer = 0 AND v_invalid_product = 0 AND v_invalid_region = 0 THEN
            p_result := 'PASS';
        ELSE
            p_result := 'FAIL';
        END IF;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_DATA_VALIDATION.VALIDATE_REFERENTIAL_INTEGRITY',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            p_result := 'FAIL';
            RAISE;
    END VALIDATE_REFERENTIAL_INTEGRITY;
    
    PROCEDURE VALIDATE_DATA_COMPLETENESS(
        p_table_name IN VARCHAR2,
        p_result OUT VARCHAR2,
        p_missing_count OUT NUMBER
    ) IS
        v_sql VARCHAR2(4000);
        v_count NUMBER;
    BEGIN
        -- Dynamic SQL to check for NULLs in key columns
        IF p_table_name = 'SALES_TRANSACTIONS' THEN
            SELECT COUNT(*) INTO v_count
            FROM SALES_TRANSACTIONS
            WHERE TRANSACTION_DATE IS NULL OR CUSTOMER_ID IS NULL OR PRODUCT_ID IS NULL;
        ELSIF p_table_name = 'CUSTOMERS' THEN
            SELECT COUNT(*) INTO v_count
            FROM CUSTOMERS
            WHERE CUSTOMER_NAME IS NULL OR CUSTOMER_CODE IS NULL;
        ELSE
            v_count := 0;
        END IF;
        
        p_missing_count := v_count;
        
        IF v_count = 0 THEN
            p_result := 'PASS';
        ELSE
            p_result := 'WARNING';
        END IF;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_DATA_VALIDATION.VALIDATE_DATA_COMPLETENESS',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            p_result := 'FAIL';
            RAISE;
    END VALIDATE_DATA_COMPLETENESS;
    
    PROCEDURE CHECK_DUPLICATES(
        p_result OUT VARCHAR2,
        p_duplicate_count OUT NUMBER
    ) IS
    BEGIN
        SELECT COUNT(*) INTO p_duplicate_count
        FROM (
            SELECT TRANSACTION_ID, COUNT(*)
            FROM SALES_TRANSACTIONS
            GROUP BY TRANSACTION_ID
            HAVING COUNT(*) > 1
        );
        
        IF p_duplicate_count = 0 THEN
            p_result := 'PASS';
        ELSE
            p_result := 'FAIL';
        END IF;
        
    EXCEPTION
        WHEN OTHERS THEN
            PKG_ERROR_LOGGING.LOG_ERROR(
                'PKG_DATA_VALIDATION.CHECK_DUPLICATES',
                'EXCEPTION',
                SQLERRM,
                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
            );
            p_result := 'FAIL';
            RAISE;
    END CHECK_DUPLICATES;
    
END PKG_DATA_VALIDATION;
/

