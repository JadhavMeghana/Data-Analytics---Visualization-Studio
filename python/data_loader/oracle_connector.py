"""
Oracle Database Connection Handler
"""

import cx_Oracle
from python.utils.config_loader import load_config, get_db_connection_string
from python.utils.logger import setup_logger

logger = setup_logger(__name__)


class OracleConnector:
    """Oracle database connection manager"""
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize Oracle connector
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            conn_string = get_db_connection_string(self.config)
            self.connection = cx_Oracle.connect(conn_string)
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to Oracle database")
        except Exception as e:
            logger.error(f"Failed to connect to Oracle database: {str(e)}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Oracle database")
    
    def execute_query(self, query, params=None):
        """
        Execute SELECT query
        
        Args:
            query: SQL query string
            params: Query parameters (dict)
            
        Returns:
            list: Query results
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def execute_procedure(self, procedure_name, params=None):
        """
        Execute PL/SQL procedure
        
        Args:
            procedure_name: Procedure name
            params: Procedure parameters (dict)
        """
        try:
            if params:
                self.cursor.callproc(procedure_name, list(params.values()))
            else:
                self.cursor.callproc(procedure_name)
            self.connection.commit()
            logger.info(f"Successfully executed procedure: {procedure_name}")
        except Exception as e:
            logger.error(f"Procedure execution failed: {str(e)}")
            self.connection.rollback()
            raise
    
    def execute_batch_insert(self, query, data):
        """
        Execute batch insert
        
        Args:
            query: INSERT query string
            data: List of tuples to insert
        """
        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            logger.info(f"Successfully inserted {len(data)} records")
        except Exception as e:
            logger.error(f"Batch insert failed: {str(e)}")
            self.connection.rollback()
            raise
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

