"""
CSV Data Loader
Loads CSV files into Oracle database
"""

import pandas as pd
from pathlib import Path
from python.data_loader.oracle_connector import OracleConnector
from python.utils.logger import setup_logger
from python.utils.config_loader import load_config

logger = setup_logger(__name__)


class CSVLoader:
    """CSV file loader for Oracle database"""
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize CSV loader
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.input_path = Path(self.config['paths']['input_data'])
    
    def load_sales_data(self, csv_file):
        """
        Load sales data from CSV into Oracle
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            int: Number of records loaded
        """
        csv_path = self.input_path / csv_file
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        logger.info(f"Loading CSV file: {csv_path}")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        logger.info(f"Read {len(df)} records from CSV")
        
        # Validate required columns
        required_columns = ['transaction_date', 'customer_id', 'product_id', 
                           'quantity', 'unit_price', 'total_amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean and prepare data
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df = df.fillna(0)
        
        # Load into Oracle
        with OracleConnector() as db:
            # Get next sequence value for transaction_id
            insert_query = """
                INSERT INTO SALES_TRANSACTIONS (
                    TRANSACTION_ID,
                    TRANSACTION_DATE,
                    CUSTOMER_ID,
                    PRODUCT_ID,
                    QUANTITY,
                    UNIT_PRICE,
                    TOTAL_AMOUNT,
                    REGION_ID,
                    DISCOUNT_PERCENTAGE,
                    LOAD_DATE
                ) VALUES (
                    SEQ_TRANSACTION_ID.NEXTVAL,
                    :1, :2, :3, :4, :5, :6, :7, :8, SYSDATE
                )
            """
            
            # Prepare data tuples
            data_tuples = [
                (
                    row['transaction_date'],
                    int(row['customer_id']),
                    int(row['product_id']),
                    float(row['quantity']),
                    float(row['unit_price']),
                    float(row['total_amount']),
                    int(row.get('region_id', 0)) if pd.notna(row.get('region_id')) else None,
                    float(row.get('discount_percentage', 0))
                )
                for _, row in df.iterrows()
            ]
            
            db.execute_batch_insert(insert_query, data_tuples)
        
        logger.info(f"Successfully loaded {len(df)} records into Oracle")
        
        # Archive file
        archive_path = Path(self.config['paths']['archive_data'])
        archive_path.mkdir(parents=True, exist_ok=True)
        archive_file = archive_path / f"{csv_path.stem}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path.rename(archive_file)
        logger.info(f"Archived file to: {archive_file}")
        
        return len(df)

