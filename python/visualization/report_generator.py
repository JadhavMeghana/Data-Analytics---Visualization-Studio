"""
Report Generator
Creates text and CSV summary reports
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from python.data_loader.oracle_connector import OracleConnector
from python.utils.logger import setup_logger
from python.utils.config_loader import load_config
from python.analytics.insight_generator import InsightGenerator

logger = setup_logger(__name__)


class ReportGenerator:
    """Report generation manager"""
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize report generator
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.summaries_path = Path(self.config['paths']['reports_summaries'])
        self.insights_path = Path(self.config['paths']['reports_insights'])
        self.summaries_path.mkdir(parents=True, exist_ok=True)
        self.insights_path.mkdir(parents=True, exist_ok=True)
        self.insight_gen = InsightGenerator(config_path)
    
    def generate_kpi_summary_csv(self):
        """
        Generate CSV summary of all KPIs
        """
        with OracleConnector() as db:
            query = """
                SELECT 
                    KPI_NAME,
                    KPI_DATE,
                    KPI_VALUE,
                    REGION_ID,
                    CALCULATION_DATE
                FROM KPI_RESULTS
                ORDER BY KPI_NAME, KPI_DATE DESC
            """
            results = db.execute_query(query)
            
            if not results:
                logger.warning("No KPI data found")
                return
            
            df = pd.DataFrame(results, columns=[
                'KPI_NAME', 'KPI_DATE', 'KPI_VALUE', 'REGION_ID', 'CALCULATION_DATE'
            ])
            
            csv_file = self.summaries_path / f'kpi_summary_{datetime.now().strftime("%Y%m%d")}.csv'
            df.to_csv(csv_file, index=False)
            
            logger.info(f"Generated KPI summary CSV: {csv_file}")
    
    def generate_text_report(self):
        """
        Generate comprehensive text report
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("ENTERPRISE SALES ANALYTICS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        with OracleConnector() as db:
            # Total Revenue
            query1 = """
                SELECT SUM(KPI_VALUE) as TOTAL_REVENUE
                FROM KPI_RESULTS
                WHERE KPI_NAME = 'MONTHLY_REVENUE_TREND'
            """
            result1 = db.execute_query(query1)
            if result1 and result1[0][0]:
                report_lines.append(f"Total Revenue: ${result1[0][0]:,.2f}")
            
            # Revenue by Region
            query2 = """
                SELECT r.REGION_NAME, SUM(k.KPI_VALUE) as REVENUE
                FROM KPI_RESULTS k
                JOIN REGIONS r ON k.REGION_ID = r.REGION_ID
                WHERE k.KPI_NAME = 'REVENUE_BY_REGION'
                GROUP BY r.REGION_NAME
                ORDER BY REVENUE DESC
            """
            result2 = db.execute_query(query2)
            if result2:
                report_lines.append("")
                report_lines.append("Revenue by Region:")
                report_lines.append("-" * 40)
                for row in result2:
                    report_lines.append(f"  {row[0]}: ${row[1]:,.2f}")
            
            # Average Transaction Value
            query3 = """
                SELECT AVG(KPI_VALUE) as AVG_VALUE
                FROM KPI_RESULTS
                WHERE KPI_NAME = 'AVG_TRANSACTION_VALUE'
            """
            result3 = db.execute_query(query3)
            if result3 and result3[0][0]:
                report_lines.append("")
                report_lines.append(f"Average Transaction Value: ${result3[0][0]:,.2f}")
        
        # Add insights
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("INSIGHTS")
        report_lines.append("=" * 80)
        insights = self.insight_gen.generate_summary_insights()
        report_lines.append(insights)
        
        report_text = "\n".join(report_lines)
        
        report_file = self.summaries_path / f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Generated text report: {report_file}")
        return report_text
    
    def generate_insight_file(self):
        """
        Generate standalone insight file
        """
        insights = self.insight_gen.generate_summary_insights()
        
        insight_file = self.insights_path / f'insights_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(insight_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("AUTOMATED INSIGHTS REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            f.write(insights)
        
        logger.info(f"Generated insight file: {insight_file}")
    
    def generate_all_reports(self):
        """Generate all reports"""
        logger.info("Generating all reports...")
        self.generate_kpi_summary_csv()
        self.generate_text_report()
        self.generate_insight_file()
        logger.info("All reports generated successfully")

