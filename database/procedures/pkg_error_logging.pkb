-- =====================================================
-- Error Logging Package Body
-- =====================================================

CREATE OR REPLACE PACKAGE BODY PKG_ERROR_LOGGING AS
    
    PROCEDURE LOG_ERROR(
        p_error_source IN VARCHAR2,
        p_error_type IN VARCHAR2,
        p_error_message IN VARCHAR2,
        p_error_stack IN CLOB DEFAULT NULL
    ) IS
    BEGIN
        INSERT INTO ERROR_LOG (
            ERROR_ID,
            ERROR_DATE,
            ERROR_SOURCE,
            ERROR_TYPE,
            ERROR_MESSAGE,
            ERROR_STACK,
            RESOLUTION_STATUS
        ) VALUES (
            SEQ_ERROR_ID.NEXTVAL,
            SYSDATE,
            p_error_source,
            p_error_type,
            SUBSTR(p_error_message, 1, 4000),
            p_error_stack,
            'PENDING'
        );
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            -- If logging fails, write to alert log (simplified)
            RAISE_APPLICATION_ERROR(-20001, 'Failed to log error: ' || SQLERRM);
    END LOG_ERROR;
    
    FUNCTION GET_ERROR_COUNT(
        p_start_date IN DATE DEFAULT SYSDATE - 7,
        p_end_date IN DATE DEFAULT SYSDATE
    ) RETURN NUMBER IS
        v_count NUMBER;
    BEGIN
        SELECT COUNT(*)
        INTO v_count
        FROM ERROR_LOG
        WHERE ERROR_DATE BETWEEN p_start_date AND p_end_date
        AND RESOLUTION_STATUS = 'PENDING';
        
        RETURN v_count;
    EXCEPTION
        WHEN OTHERS THEN
            RETURN 0;
    END GET_ERROR_COUNT;
    
    PROCEDURE UPDATE_ERROR_STATUS(
        p_error_id IN NUMBER,
        p_status IN VARCHAR2
    ) IS
    BEGIN
        UPDATE ERROR_LOG
        SET RESOLUTION_STATUS = p_status
        WHERE ERROR_ID = p_error_id;
        
        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20002, 'Error ID not found: ' || p_error_id);
        END IF;
        
        COMMIT;
    END UPDATE_ERROR_STATUS;
    
END PKG_ERROR_LOGGING;
/

