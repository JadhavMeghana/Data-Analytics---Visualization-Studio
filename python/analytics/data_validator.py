"""
Data Validator
Calls PL/SQL validation procedures
"""

import cx_Oracle
from python.data_loader.oracle_connector import OracleConnector
from python.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataValidator:
    """Data validation manager"""
    
    def __init__(self):
        """Initialize data validator"""
        pass
    
    def validate_all(self):
        """
        Run all validation checks
        
        Returns:
            dict: Validation results
        """
        results = {}
        
        with OracleConnector() as db:
            cursor = db.cursor
            
            # Validate Sales Data
            logger.info("Validating sales data...")
            result = cursor.var(str)
            records_checked = cursor.var(int)
            records_passed = cursor.var(int)
            records_failed = cursor.var(int)
            
            cursor.callproc(
                'PKG_DATA_VALIDATION.VALIDATE_SALES_DATA',
                [None, result, records_checked, records_passed, records_failed]
            )
            
            results['sales_data'] = {
                'status': result.getvalue(),
                'checked': records_checked.getvalue(),
                'passed': records_passed.getvalue(),
                'failed': records_failed.getvalue()
            }
            
            # Validate Referential Integrity
            logger.info("Validating referential integrity...")
            ref_result = cursor.var(str)
            error_details = cursor.var(cx_Oracle.CLOB)
            
            cursor.callproc(
                'PKG_DATA_VALIDATION.VALIDATE_REFERENTIAL_INTEGRITY',
                [ref_result, error_details]
            )
            
            results['referential_integrity'] = {
                'status': ref_result.getvalue(),
                'details': str(error_details.getvalue()) if error_details.getvalue() else ''
            }
            
            # Check Duplicates
            logger.info("Checking for duplicates...")
            dup_result = cursor.var(str)
            dup_count = cursor.var(int)
            
            cursor.callproc(
                'PKG_DATA_VALIDATION.CHECK_DUPLICATES',
                [dup_result, dup_count]
            )
            
            results['duplicates'] = {
                'status': dup_result.getvalue(),
                'count': dup_count.getvalue()
            }
        
        logger.info(f"Validation complete. Results: {results}")
        return results

