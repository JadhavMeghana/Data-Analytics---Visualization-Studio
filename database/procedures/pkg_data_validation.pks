-- =====================================================
-- Data Validation Package Specification
-- =====================================================

CREATE OR REPLACE PACKAGE PKG_DATA_VALIDATION AS
    
    -- Validate sales transactions data
    PROCEDURE VALIDATE_SALES_DATA(
        p_validation_date IN DATE DEFAULT SYSDATE,
        p_result OUT VARCHAR2,
        p_records_checked OUT NUMBER,
        p_records_passed OUT NUMBER,
        p_records_failed OUT NUMBER
    );
    
    -- Validate referential integrity
    PROCEDURE VALIDATE_REFERENTIAL_INTEGRITY(
        p_result OUT VARCHAR2,
        p_error_details OUT CLOB
    );
    
    -- Validate data completeness
    PROCEDURE VALIDATE_DATA_COMPLETENESS(
        p_table_name IN VARCHAR2,
        p_result OUT VARCHAR2,
        p_missing_count OUT NUMBER
    );
    
    -- Check for duplicate transactions
    PROCEDURE CHECK_DUPLICATES(
        p_result OUT VARCHAR2,
        p_duplicate_count OUT NUMBER
    );
    
END PKG_DATA_VALIDATION;
/

