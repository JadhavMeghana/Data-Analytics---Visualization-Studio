"""
Insight Generator
AI-like rule-based insights generation
"""

import pandas as pd
from datetime import datetime, timedelta
from python.data_loader.oracle_connector import OracleConnector
from python.utils.logger import setup_logger
from python.utils.config_loader import load_config

logger = setup_logger(__name__)


class InsightGenerator:
    """Rule-based insight generator"""
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize insight generator
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.thresholds = self.config.get('kpi_thresholds', {})
    
    def detect_outliers(self, kpi_name, threshold_percent=None):
        """
        Detect outliers in KPI values
        
        Args:
            kpi_name: Name of KPI
            threshold_percent: Percentage threshold for anomaly
            
        Returns:
            list: List of outlier records
        """
        if threshold_percent is None:
            threshold_percent = self.thresholds.get('revenue_anomaly_percentage', 20)
        
        with OracleConnector() as db:
            query = """
                SELECT KPI_DATE, KPI_VALUE, REGION_ID
                FROM KPI_RESULTS
                WHERE KPI_NAME = :kpi_name
                ORDER BY KPI_DATE DESC
            """
            results = db.execute_query(query, {'kpi_name': kpi_name})
            
            if not results:
                return []
            
            df = pd.DataFrame(results, columns=['KPI_DATE', 'KPI_VALUE', 'REGION_ID'])
            
            # Calculate mean and standard deviation
            mean_value = df['KPI_VALUE'].mean()
            std_value = df['KPI_VALUE'].std()
            
            # Identify outliers (values beyond threshold)
            threshold = mean_value * (threshold_percent / 100)
            outliers = df[
                (df['KPI_VALUE'] > mean_value + threshold) |
                (df['KPI_VALUE'] < mean_value - threshold)
            ]
            
            return outliers.to_dict('records')
    
    def detect_trends(self, kpi_name, periods=None):
        """
        Detect trends in KPI values
        
        Args:
            kpi_name: Name of KPI
            periods: Number of periods to analyze
            
        Returns:
            str: Trend description
        """
        if periods is None:
            periods = self.thresholds.get('trend_detection_periods', 3)
        
        with OracleConnector() as db:
            query = """
                SELECT KPI_DATE, KPI_VALUE
                FROM KPI_RESULTS
                WHERE KPI_NAME = :kpi_name
                ORDER BY KPI_DATE DESC
                FETCH FIRST :periods ROWS ONLY
            """
            results = db.execute_query(query, {'kpi_name': kpi_name, 'periods': periods})
            
            if len(results) < periods:
                return "Insufficient data for trend analysis"
            
            df = pd.DataFrame(results, columns=['KPI_DATE', 'KPI_VALUE'])
            df = df.sort_values('KPI_DATE')
            
            # Calculate trend
            values = df['KPI_VALUE'].values
            if len(values) >= 2:
                trend = "increasing" if values[-1] > values[0] else "decreasing"
                change_percent = ((values[-1] - values[0]) / values[0]) * 100
                
                return f"Trend: {trend} ({change_percent:.2f}% change over {periods} periods)"
            
            return "No clear trend detected"
    
    def generate_summary_insights(self):
        """
        Generate comprehensive summary insights
        
        Returns:
            str: Formatted insight summary
        """
        insights = []
        
        # Revenue by Region insights
        outliers = self.detect_outliers('REVENUE_BY_REGION')
        if outliers:
            insights.append(f"⚠️ Found {len(outliers)} revenue outliers by region")
        
        # Monthly trend
        trend = self.detect_trends('MONTHLY_REVENUE_TREND')
        insights.append(f"📈 Monthly Revenue: {trend}")
        
        # Top customers analysis
        with OracleConnector() as db:
            query = """
                SELECT COUNT(*) as top_customer_count
                FROM KPI_RESULTS
                WHERE KPI_NAME = 'TOP_CUSTOMERS'
                AND KPI_DATE >= SYSDATE - 7
            """
            results = db.execute_query(query)
            if results and results[0][0] > 0:
                insights.append(f"👥 Top customers analysis available for last 7 days")
        
        summary = "\n".join(insights) if insights else "No significant insights detected"
        
        logger.info(f"Generated insights: {summary}")
        return summary

