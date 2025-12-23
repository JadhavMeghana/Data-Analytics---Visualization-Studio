"""
Main Pipeline Orchestrator
End-to-end data analytics pipeline
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.data_loader.csv_loader import CSVLoader
from python.analytics.data_validator import DataValidator
from python.analytics.kpi_calculator import KPICalculator
from python.visualization.chart_generator import ChartGenerator
from python.visualization.report_generator import ReportGenerator
from python.utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/app.log')


def main():
    """
    Main pipeline execution
    """
    try:
        logger.info("=" * 80)
        logger.info("Starting Enterprise Sales Analytics Pipeline")
        logger.info("=" * 80)
        
        # Step 1: Load data (if CSV file provided)
        if len(sys.argv) > 1:
            csv_file = sys.argv[1]
            logger.info(f"Loading data from: {csv_file}")
            loader = CSVLoader()
            records_loaded = loader.load_sales_data(csv_file)
            logger.info(f"Loaded {records_loaded} records")
        else:
            logger.info("No CSV file provided, skipping data load step")
        
        # Step 2: Validate data
        logger.info("Step 2: Validating data...")
        validator = DataValidator()
        validation_results = validator.validate_all()
        logger.info(f"Validation results: {validation_results}")
        
        # Step 3: Calculate KPIs
        logger.info("Step 3: Calculating KPIs...")
        kpi_calc = KPICalculator()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        kpi_calc.calculate_all_kpis(start_date=start_date, end_date=end_date)
        
        # Step 4: Generate charts
        logger.info("Step 4: Generating charts...")
        chart_gen = ChartGenerator()
        chart_gen.generate_all_charts()
        
        # Step 5: Generate reports
        logger.info("Step 5: Generating reports...")
        report_gen = ReportGenerator()
        report_gen.generate_all_reports()
        
        logger.info("=" * 80)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

