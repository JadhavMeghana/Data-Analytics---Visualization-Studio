"""
KPI Calculator
Calls PL/SQL procedures to calculate KPIs
"""

import cx_Oracle
from datetime import datetime, timedelta
from python.data_loader.oracle_connector import OracleConnector
from python.utils.logger import setup_logger

logger = setup_logger(__name__)


class KPICalculator:
    """KPI calculation manager"""
    
    def __init__(self):
        """Initialize KPI calculator"""
        pass
    
    def calculate_all_kpis(self, start_date=None, end_date=None, top_n=10):
        """
        Calculate all KPIs
        
        Args:
            start_date: Start date (datetime or None for last 30 days)
            end_date: End date (datetime or None for today)
            top_n: Number of top customers to calculate
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        logger.info(f"Calculating KPIs from {start_date.date()} to {end_date.date()}")
        
        with OracleConnector() as db:
            try:
                # Revenue by Region
                logger.info("Calculating Revenue by Region...")
                db.cursor.callproc(
                    'PKG_KPI_CALCULATIONS.CALC_REVENUE_BY_REGION',
                    [start_date, end_date]
                )
                db.connection.commit()
                
                # Monthly Revenue Trend
                logger.info("Calculating Monthly Revenue Trend...")
                db.cursor.callproc(
                    'PKG_KPI_CALCULATIONS.CALC_MONTHLY_REVENUE_TREND',
                    [start_date, end_date]
                )
                db.connection.commit()
                
                # Top Customers
                logger.info(f"Calculating Top {top_n} Customers...")
                db.cursor.callproc(
                    'PKG_KPI_CALCULATIONS.CALC_TOP_CUSTOMERS',
                    [start_date, end_date, top_n]
                )
                db.connection.commit()
                
                # Product Performance
                logger.info("Calculating Product Performance...")
                db.cursor.callproc(
                    'PKG_KPI_CALCULATIONS.CALC_PRODUCT_PERFORMANCE',
                    [start_date, end_date]
                )
                db.connection.commit()
                
                # Average Transaction Value
                logger.info("Calculating Average Transaction Value...")
                db.cursor.callproc(
                    'PKG_KPI_CALCULATIONS.CALC_AVG_TRANSACTION_VALUE',
                    [start_date, end_date]
                )
                db.connection.commit()
                
                logger.info("All KPIs calculated successfully")
                
            except Exception as e:
                logger.error(f"Error calculating KPIs: {str(e)}")
                db.connection.rollback()
                raise
    
    def get_kpi_results(self, kpi_name, start_date=None, end_date=None):
        """
        Retrieve KPI results from database
        
        Args:
            kpi_name: Name of KPI
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            list: KPI results
        """
        with OracleConnector() as db:
            result_cursor = db.cursor.callfunc(
                'PKG_KPI_CALCULATIONS.GET_KPI_RESULTS',
                cx_Oracle.CURSOR,
                [kpi_name, start_date, end_date]
            )
            
            columns = [desc[0] for desc in result_cursor.description]
            results = []
            for row in result_cursor:
                results.append(dict(zip(columns, row)))
            
            return results

