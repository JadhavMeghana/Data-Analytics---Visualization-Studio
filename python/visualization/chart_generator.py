"""
Chart Generator
Creates visualizations using matplotlib, seaborn, and plotly
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from python.data_loader.oracle_connector import OracleConnector
from python.utils.logger import setup_logger
from python.utils.config_loader import load_config

logger = setup_logger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ChartGenerator:
    """Chart generation manager"""
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize chart generator
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.charts_path = Path(self.config['paths']['reports_charts'])
        self.charts_path.mkdir(parents=True, exist_ok=True)
    
    def plot_revenue_by_region(self, start_date=None, end_date=None):
        """
        Generate revenue by region chart
        
        Args:
            start_date: Start date filter
            end_date: End date filter
        """
        with OracleConnector() as db:
            query = """
                SELECT r.REGION_NAME, SUM(k.KPI_VALUE) as TOTAL_REVENUE
                FROM KPI_RESULTS k
                JOIN REGIONS r ON k.REGION_ID = r.REGION_ID
                WHERE k.KPI_NAME = 'REVENUE_BY_REGION'
                AND (:start_date IS NULL OR k.KPI_DATE >= :start_date)
                AND (:end_date IS NULL OR k.KPI_DATE <= :end_date)
                GROUP BY r.REGION_NAME
                ORDER BY TOTAL_REVENUE DESC
            """
            results = db.execute_query(query, {'start_date': start_date, 'end_date': end_date})
            
            if not results:
                logger.warning("No data found for revenue by region")
                return
            
            df = pd.DataFrame(results, columns=['REGION_NAME', 'TOTAL_REVENUE'])
            
            # Matplotlib chart
            plt.figure(figsize=(10, 6))
            plt.bar(df['REGION_NAME'], df['TOTAL_REVENUE'], color='steelblue')
            plt.title('Revenue by Region', fontsize=16, fontweight='bold')
            plt.xlabel('Region', fontsize=12)
            plt.ylabel('Total Revenue', fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_file = self.charts_path / 'revenue_by_region.png'
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved chart: {chart_file}")
    
    def plot_monthly_trend(self):
        """
        Generate monthly revenue trend chart
        """
        with OracleConnector() as db:
            query = """
                SELECT KPI_DATE, KPI_VALUE
                FROM KPI_RESULTS
                WHERE KPI_NAME = 'MONTHLY_REVENUE_TREND'
                ORDER BY KPI_DATE
            """
            results = db.execute_query(query)
            
            if not results:
                logger.warning("No data found for monthly trend")
                return
            
            df = pd.DataFrame(results, columns=['KPI_DATE', 'KPI_VALUE'])
            df['KPI_DATE'] = pd.to_datetime(df['KPI_DATE'])
            
            # Seaborn line chart
            plt.figure(figsize=(12, 6))
            sns.lineplot(data=df, x='KPI_DATE', y='KPI_VALUE', marker='o', linewidth=2)
            plt.title('Monthly Revenue Trend', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Revenue', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            chart_file = self.charts_path / 'monthly_revenue_trend.png'
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved chart: {chart_file}")
    
    def plot_top_customers(self, top_n=10):
        """
        Generate top customers chart
        
        Args:
            top_n: Number of top customers to show
        """
        with OracleConnector() as db:
            query = """
                SELECT c.CUSTOMER_NAME, SUM(s.TOTAL_AMOUNT) as REVENUE
                FROM SALES_TRANSACTIONS s
                JOIN CUSTOMERS c ON s.CUSTOMER_ID = c.CUSTOMER_ID
                GROUP BY c.CUSTOMER_NAME
                ORDER BY REVENUE DESC
                FETCH FIRST :top_n ROWS ONLY
            """
            results = db.execute_query(query, {'top_n': top_n})
            
            if not results:
                logger.warning("No data found for top customers")
                return
            
            df = pd.DataFrame(results, columns=['CUSTOMER_NAME', 'REVENUE'])
            
            # Horizontal bar chart
            plt.figure(figsize=(10, 8))
            plt.barh(df['CUSTOMER_NAME'], df['REVENUE'], color='coral')
            plt.title(f'Top {top_n} Customers by Revenue', fontsize=16, fontweight='bold')
            plt.xlabel('Revenue', fontsize=12)
            plt.ylabel('Customer', fontsize=12)
            plt.tight_layout()
            
            chart_file = self.charts_path / 'top_customers.png'
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved chart: {chart_file}")
    
    def create_interactive_dashboard(self):
        """
        Create interactive Plotly dashboard
        """
        with OracleConnector() as db:
            # Get revenue by region
            query1 = """
                SELECT r.REGION_NAME, SUM(k.KPI_VALUE) as TOTAL_REVENUE
                FROM KPI_RESULTS k
                JOIN REGIONS r ON k.REGION_ID = r.REGION_ID
                WHERE k.KPI_NAME = 'REVENUE_BY_REGION'
                GROUP BY r.REGION_NAME
            """
            region_data = db.execute_query(query1)
            
            # Get monthly trend
            query2 = """
                SELECT KPI_DATE, KPI_VALUE
                FROM KPI_RESULTS
                WHERE KPI_NAME = 'MONTHLY_REVENUE_TREND'
                ORDER BY KPI_DATE
            """
            trend_data = db.execute_query(query2)
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Revenue by Region', 'Monthly Revenue Trend'),
                specs=[[{"type": "bar"}], [{"type": "scatter"}]]
            )
            
            # Bar chart for regions
            if region_data:
                df_regions = pd.DataFrame(region_data, columns=['REGION_NAME', 'TOTAL_REVENUE'])
                fig.add_trace(
                    go.Bar(x=df_regions['REGION_NAME'], y=df_regions['TOTAL_REVENUE'],
                          name='Revenue', marker_color='steelblue'),
                    row=1, col=1
                )
            
            # Line chart for trend
            if trend_data:
                df_trend = pd.DataFrame(trend_data, columns=['KPI_DATE', 'KPI_VALUE'])
                df_trend['KPI_DATE'] = pd.to_datetime(df_trend['KPI_DATE'])
                fig.add_trace(
                    go.Scatter(x=df_trend['KPI_DATE'], y=df_trend['KPI_VALUE'],
                             mode='lines+markers', name='Revenue Trend',
                             line=dict(color='coral', width=2)),
                    row=2, col=1
                )
            
            fig.update_layout(
                height=800,
                title_text="Sales Analytics Dashboard",
                showlegend=True
            )
            
            dashboard_file = self.charts_path / 'interactive_dashboard.html'
            fig.write_html(str(dashboard_file))
            
            logger.info(f"Saved interactive dashboard: {dashboard_file}")
    
    def generate_all_charts(self):
        """Generate all charts"""
        logger.info("Generating all charts...")
        self.plot_revenue_by_region()
        self.plot_monthly_trend()
        self.plot_top_customers()
        self.create_interactive_dashboard()
        logger.info("All charts generated successfully")

