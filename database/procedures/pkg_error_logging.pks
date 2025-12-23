-- =====================================================
-- Error Logging Package Specification
-- =====================================================

CREATE OR REPLACE PACKAGE PKG_ERROR_LOGGING AS
    
    -- Log an error
    PROCEDURE LOG_ERROR(
        p_error_source IN VARCHAR2,
        p_error_type IN VARCHAR2,
        p_error_message IN VARCHAR2,
        p_error_stack IN CLOB DEFAULT NULL
    );
    
    -- Get error count for a date range
    FUNCTION GET_ERROR_COUNT(
        p_start_date IN DATE DEFAULT SYSDATE - 7,
        p_end_date IN DATE DEFAULT SYSDATE
    ) RETURN NUMBER;
    
    -- Update error resolution status
    PROCEDURE UPDATE_ERROR_STATUS(
        p_error_id IN NUMBER,
        p_status IN VARCHAR2
    );
    
END PKG_ERROR_LOGGING;
/

