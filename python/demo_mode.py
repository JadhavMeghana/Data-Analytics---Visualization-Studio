"""
Demo Mode - Runs application without Oracle database
Uses in-memory data to demonstrate full functionality
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.utils.logger import setup_logger
from python.visualization.chart_generator import ChartGenerator
from python.visualization.report_generator import ReportGenerator

logger = setup_logger(__name__, 'logs/demo.log')


class DemoDataGenerator:
    """Generate demo data for testing without Oracle"""
    
    def __init__(self):
        self.regions = [
            {'REGION_ID': 1, 'REGION_NAME': 'North America', 'REGION_CODE': 'NA'},
            {'REGION_ID': 2, 'REGION_NAME': 'Europe', 'REGION_CODE': 'EU'},
            {'REGION_ID': 3, 'REGION_NAME': 'Asia Pacific', 'REGION_CODE': 'APAC'},
            {'REGION_ID': 4, 'REGION_NAME': 'Middle East', 'REGION_CODE': 'ME'}
        ]
        
        self.customers = [
            {'CUSTOMER_ID': 1, 'CUSTOMER_NAME': 'Acme Corp', 'REGION_ID': 1},
            {'CUSTOMER_ID': 2, 'CUSTOMER_NAME': 'Tech Solutions Inc', 'REGION_ID': 2},
            {'CUSTOMER_ID': 3, 'CUSTOMER_NAME': 'Global Enterprises', 'REGION_ID': 3},
            {'CUSTOMER_ID': 4, 'CUSTOMER_NAME': 'Digital Services Ltd', 'REGION_ID': 4},
            {'CUSTOMER_ID': 5, 'CUSTOMER_NAME': 'Innovation Hub', 'REGION_ID': 1},
            {'CUSTOMER_ID': 6, 'CUSTOMER_NAME': 'Mega Corp', 'REGION_ID': 2},
            {'CUSTOMER_ID': 7, 'CUSTOMER_NAME': 'StartupXYZ', 'REGION_ID': 3},
            {'CUSTOMER_ID': 8, 'CUSTOMER_NAME': 'Enterprise Solutions', 'REGION_ID': 4},
            {'CUSTOMER_ID': 9, 'CUSTOMER_NAME': 'Tech Giants', 'REGION_ID': 1},
            {'CUSTOMER_ID': 10, 'CUSTOMER_NAME': 'Future Systems', 'REGION_ID': 2}
        ]
        
        self.products = [
            {'PRODUCT_ID': 101, 'PRODUCT_NAME': 'Software License', 'CATEGORY': 'Software', 'UNIT_PRICE': 1000},
            {'PRODUCT_ID': 102, 'PRODUCT_NAME': 'Cloud Service', 'CATEGORY': 'Cloud', 'UNIT_PRICE': 500},
            {'PRODUCT_ID': 103, 'PRODUCT_NAME': 'Consulting Hours', 'CATEGORY': 'Services', 'UNIT_PRICE': 150},
            {'PRODUCT_ID': 104, 'PRODUCT_NAME': 'Hardware Equipment', 'CATEGORY': 'Hardware', 'UNIT_PRICE': 2000},
            {'PRODUCT_ID': 105, 'PRODUCT_NAME': 'Support Package', 'CATEGORY': 'Services', 'UNIT_PRICE': 300}
        ]
    
    def generate_sales_data(self, num_days=90):
        """Generate sample sales transactions"""
        transactions = []
        start_date = datetime.now() - timedelta(days=num_days)
        
        np.random.seed(42)  # For reproducibility
        
        for day in range(num_days):
            date = start_date + timedelta(days=day)
            num_transactions = np.random.randint(5, 20)
            
            for _ in range(num_transactions):
                customer = np.random.choice(self.customers)
                product = np.random.choice(self.products)
                region_id = customer['REGION_ID']
                quantity = np.random.randint(1, 50)
                unit_price = product['UNIT_PRICE'] * (0.8 + np.random.random() * 0.4)  # 20% variance
                discount = np.random.choice([0, 0, 0, 5, 10])  # Mostly no discount
                total_amount = quantity * unit_price * (1 - discount / 100)
                
                transactions.append({
                    'TRANSACTION_DATE': date,
                    'CUSTOMER_ID': customer['CUSTOMER_ID'],
                    'PRODUCT_ID': product['PRODUCT_ID'],
                    'QUANTITY': quantity,
                    'UNIT_PRICE': unit_price,
                    'TOTAL_AMOUNT': total_amount,
                    'REGION_ID': region_id,
                    'DISCOUNT_PERCENTAGE': discount
                })
        
        return pd.DataFrame(transactions)
    
    def generate_kpi_results(self, sales_df):
        """Generate KPI results from sales data"""
        kpi_results = []
        
        # Revenue by Region
        revenue_by_region = sales_df.groupby(['REGION_ID', sales_df['TRANSACTION_DATE'].dt.date])['TOTAL_AMOUNT'].sum().reset_index()
        for _, row in revenue_by_region.iterrows():
            kpi_results.append({
                'KPI_NAME': 'REVENUE_BY_REGION',
                'KPI_VALUE': row['TOTAL_AMOUNT'],
                'KPI_DATE': row['TRANSACTION_DATE'],
                'REGION_ID': int(row['REGION_ID']),
                'CALCULATION_DATE': datetime.now()
            })
        
        # Monthly Revenue Trend
        monthly_revenue = sales_df.groupby(sales_df['TRANSACTION_DATE'].dt.to_period('M'))['TOTAL_AMOUNT'].sum()
        for period, value in monthly_revenue.items():
            kpi_results.append({
                'KPI_NAME': 'MONTHLY_REVENUE_TREND',
                'KPI_VALUE': value,
                'KPI_DATE': period.to_timestamp(),
                'REGION_ID': None,
                'CALCULATION_DATE': datetime.now()
            })
        
        # Top Customers
        top_customers = sales_df.groupby('CUSTOMER_ID')['TOTAL_AMOUNT'].sum().nlargest(10)
        for customer_id, value in top_customers.items():
            kpi_results.append({
                'KPI_NAME': 'TOP_CUSTOMERS',
                'KPI_VALUE': value,
                'KPI_DATE': datetime.now().date(),
                'REGION_ID': None,
                'CALCULATION_DATE': datetime.now()
            })
        
        # Average Transaction Value
        daily_avg = sales_df.groupby(sales_df['TRANSACTION_DATE'].dt.date)['TOTAL_AMOUNT'].mean()
        for date, value in daily_avg.items():
            kpi_results.append({
                'KPI_NAME': 'AVG_TRANSACTION_VALUE',
                'KPI_VALUE': value,
                'KPI_DATE': date,
                'REGION_ID': None,
                'CALCULATION_DATE': datetime.now()
            })
        
        return pd.DataFrame(kpi_results)


class DemoOracleConnector:
    """Mock Oracle connector for demo mode"""
    
    def __init__(self, sales_df, kpi_df, regions, customers, products):
        self.sales_df = sales_df
        self.kpi_df = kpi_df
        self.regions = pd.DataFrame(regions)
        self.customers = pd.DataFrame(customers)
        self.products = pd.DataFrame(products)
        self.connection = True  # Mock connection
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def execute_query(self, query, params=None):
        """Mock query execution"""
        # Parse simple queries and return mock data
        if 'REGIONS' in query and ('REVENUE_BY_REGION' in query or 'REGION_NAME' in query):
            # Revenue by region query
            result_df = self.kpi_df[self.kpi_df['KPI_NAME'] == 'REVENUE_BY_REGION'].copy()
            if len(result_df) > 0:
                result_df = result_df.merge(self.regions, on='REGION_ID', how='left')
                result_df = result_df.groupby('REGION_NAME')['KPI_VALUE'].sum().reset_index()
                result_df.columns = ['REGION_NAME', 'TOTAL_REVENUE']
                return [tuple(row) for row in result_df.values]
            else:
                # Fallback: calculate from sales data
                region_revenue = self.sales_df.groupby('REGION_ID')['TOTAL_AMOUNT'].sum().reset_index()
                region_revenue = region_revenue.merge(self.regions, on='REGION_ID', how='left')
                region_revenue = region_revenue[['REGION_NAME', 'TOTAL_AMOUNT']]
                region_revenue.columns = ['REGION_NAME', 'TOTAL_REVENUE']
                return [tuple(row) for row in region_revenue.values]
        
        elif 'MONTHLY_REVENUE_TREND' in query:
            result_df = self.kpi_df[self.kpi_df['KPI_NAME'] == 'MONTHLY_REVENUE_TREND'].copy()
            if len(result_df) > 0:
                result_df = result_df.sort_values('KPI_DATE')
                return [(row['KPI_DATE'], row['KPI_VALUE']) for _, row in result_df.iterrows()]
            else:
                # Fallback: calculate from sales data
                monthly_revenue = self.sales_df.groupby(self.sales_df['TRANSACTION_DATE'].dt.to_period('M'))['TOTAL_AMOUNT'].sum()
                return [(period.to_timestamp(), value) for period, value in monthly_revenue.items()]
        
        elif 'TOP_CUSTOMERS' in query or 'CUSTOMER_NAME' in query:
            # Top customers query - get customer revenue and match with customer names
            customer_revenue = self.sales_df.groupby('CUSTOMER_ID')['TOTAL_AMOUNT'].sum().reset_index()
            customer_revenue = customer_revenue.merge(self.customers, on='CUSTOMER_ID', how='left')
            customer_revenue = customer_revenue.nlargest(10, 'TOTAL_AMOUNT')
            return [(row['CUSTOMER_NAME'], row['TOTAL_AMOUNT']) for _, row in customer_revenue.iterrows()]
        
        elif 'KPI_RESULTS' in query and 'KPI_NAME' in query:
            # Generic KPI results query
            kpi_name = params.get('kpi_name', '') if params else ''
            result_df = self.kpi_df[self.kpi_df['KPI_NAME'] == kpi_name].copy() if kpi_name else self.kpi_df.copy()
            return [(row['KPI_ID'] if 'KPI_ID' in row else 0, 
                    row['KPI_NAME'], 
                    row['KPI_VALUE'], 
                    row['KPI_DATE'], 
                    row['REGION_ID'], 
                    row['CALCULATION_DATE']) for _, row in result_df.iterrows()]
        
        elif 'SUM(KPI_VALUE)' in query and 'MONTHLY_REVENUE_TREND' in query:
            total = self.kpi_df[self.kpi_df['KPI_NAME'] == 'MONTHLY_REVENUE_TREND']['KPI_VALUE'].sum()
            return [(total,)]
        
        elif 'AVG(KPI_VALUE)' in query and 'AVG_TRANSACTION_VALUE' in query:
            avg = self.kpi_df[self.kpi_df['KPI_NAME'] == 'AVG_TRANSACTION_VALUE']['KPI_VALUE'].mean()
            return [(avg,)]
        
        else:
            return []


def run_demo():
    """Run the application in demo mode"""
    logger.info("=" * 80)
    logger.info("Starting Enterprise Sales Analytics - DEMO MODE")
    logger.info("=" * 80)
    logger.info("Note: Running without Oracle database using simulated data")
    logger.info("=" * 80)
    
    try:
        # Generate demo data
        logger.info("Step 1: Generating demo data...")
        data_gen = DemoDataGenerator()
        sales_df = data_gen.generate_sales_data(num_days=90)
        logger.info(f"Generated {len(sales_df)} sales transactions")
        
        # Generate KPI results
        logger.info("Step 2: Calculating KPIs...")
        kpi_df = data_gen.generate_kpi_results(sales_df)
        logger.info(f"Generated {len(kpi_df)} KPI records")
        
        # Create mock connector
        mock_db = DemoOracleConnector(
            sales_df, 
            kpi_df, 
            data_gen.regions, 
            data_gen.customers, 
            data_gen.products
        )
        
        # Monkey patch the ChartGenerator to use mock database
        original_init = ChartGenerator.__init__
        original_report_init = ReportGenerator.__init__
        
        def mock_chart_init(self, config_path='config.yaml'):
            from python.utils.config_loader import load_config
            from pathlib import Path
            self.config = load_config(config_path)
            self.charts_path = Path(self.config['paths']['reports_charts'])
            self.charts_path.mkdir(parents=True, exist_ok=True)
            self._mock_db = mock_db
        
        def mock_report_init(self, config_path='config.yaml'):
            from python.utils.config_loader import load_config
            from pathlib import Path
            from python.analytics.insight_generator import InsightGenerator
            self.config = load_config(config_path)
            self.summaries_path = Path(self.config['paths']['reports_summaries'])
            self.insights_path = Path(self.config['paths']['reports_insights'])
            self.summaries_path.mkdir(parents=True, exist_ok=True)
            self.insights_path.mkdir(parents=True, exist_ok=True)
            self.insight_gen = None  # Skip insight generation for demo
            self._mock_db = mock_db
        
        ChartGenerator.__init__ = mock_chart_init
        ReportGenerator.__init__ = mock_report_init
        
        # Override execute_query in chart generator methods
        original_plot_revenue = ChartGenerator.plot_revenue_by_region
        original_plot_trend = ChartGenerator.plot_monthly_trend
        original_plot_customers = ChartGenerator.plot_top_customers
        original_create_dashboard = ChartGenerator.create_interactive_dashboard
        
        def mock_plot_revenue(self, start_date=None, end_date=None):
            results = self._mock_db.execute_query("SELECT r.REGION_NAME, SUM(k.KPI_VALUE) FROM KPI_RESULTS k JOIN REGIONS r")
            if not results:
                logger.warning("No data found for revenue by region")
                return
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.DataFrame(results, columns=['REGION_NAME', 'TOTAL_REVENUE'])
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
        
        def mock_plot_trend(self):
            results = self._mock_db.execute_query("SELECT KPI_DATE, KPI_VALUE FROM KPI_RESULTS WHERE KPI_NAME = 'MONTHLY_REVENUE_TREND'")
            if not results:
                logger.warning("No data found for monthly trend")
                return
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt
            df = pd.DataFrame(results, columns=['KPI_DATE', 'KPI_VALUE'])
            df['KPI_DATE'] = pd.to_datetime(df['KPI_DATE'])
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
        
        def mock_plot_customers(self, top_n=10):
            results = self._mock_db.execute_query("SELECT c.CUSTOMER_NAME, k.KPI_VALUE")
            if not results:
                logger.warning("No data found for top customers")
                return
            import pandas as pd
            import matplotlib.pyplot as plt
            df = pd.DataFrame(results, columns=['CUSTOMER_NAME', 'REVENUE'])
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
        
        def mock_create_dashboard(self):
            import pandas as pd
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            region_data = self._mock_db.execute_query("SELECT r.REGION_NAME, SUM(k.KPI_VALUE)")
            trend_data = self._mock_db.execute_query("SELECT KPI_DATE, KPI_VALUE FROM KPI_RESULTS")
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Revenue by Region', 'Monthly Revenue Trend'),
                specs=[[{"type": "bar"}], [{"type": "scatter"}]]
            )
            
            if region_data:
                df_regions = pd.DataFrame(region_data, columns=['REGION_NAME', 'TOTAL_REVENUE'])
                fig.add_trace(
                    go.Bar(x=df_regions['REGION_NAME'], y=df_regions['TOTAL_REVENUE'],
                          name='Revenue', marker_color='steelblue'),
                    row=1, col=1
                )
            
            if trend_data:
                df_trend = pd.DataFrame(trend_data, columns=['KPI_DATE', 'KPI_VALUE'])
                df_trend['KPI_DATE'] = pd.to_datetime(df_trend['KPI_DATE'])
                fig.add_trace(
                    go.Scatter(x=df_trend['KPI_DATE'], y=df_trend['KPI_VALUE'],
                             mode='lines+markers', name='Revenue Trend',
                             line=dict(color='coral', width=2)),
                    row=2, col=1
                )
            
            fig.update_layout(height=800, title_text="Sales Analytics Dashboard", showlegend=True)
            dashboard_file = self.charts_path / 'interactive_dashboard.html'
            fig.write_html(str(dashboard_file))
            logger.info(f"Saved interactive dashboard: {dashboard_file}")
        
        ChartGenerator.plot_revenue_by_region = mock_plot_revenue
        ChartGenerator.plot_monthly_trend = mock_plot_trend
        ChartGenerator.plot_top_customers = mock_plot_customers
        ChartGenerator.create_interactive_dashboard = mock_create_dashboard
        
        # Generate charts
        logger.info("Step 3: Generating charts...")
        chart_gen = ChartGenerator()
        chart_gen.generate_all_charts()
        
        # Generate reports
        logger.info("Step 4: Generating reports...")
        report_gen = ReportGenerator()
        
        # Override report generation methods
        def mock_generate_csv(self):
            import pandas as pd
            from datetime import datetime
            df = self._mock_db.kpi_df.copy()
            csv_file = self.summaries_path / f'kpi_summary_{datetime.now().strftime("%Y%m%d")}.csv'
            df.to_csv(csv_file, index=False)
            logger.info(f"Generated KPI summary CSV: {csv_file}")
        
        def mock_generate_text(self):
            from datetime import datetime
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("ENTERPRISE SALES ANALYTICS REPORT (DEMO MODE)")
            report_lines.append("=" * 80)
            report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            total_revenue = self._mock_db.kpi_df[self._mock_db.kpi_df['KPI_NAME'] == 'MONTHLY_REVENUE_TREND']['KPI_VALUE'].sum()
            report_lines.append(f"Total Revenue: ${total_revenue:,.2f}")
            
            region_revenue = self._mock_db.kpi_df[self._mock_db.kpi_df['KPI_NAME'] == 'REVENUE_BY_REGION'].groupby('REGION_ID')['KPI_VALUE'].sum()
            report_lines.append("")
            report_lines.append("Revenue by Region:")
            report_lines.append("-" * 40)
            for region_id, revenue in region_revenue.items():
                region_name = self._mock_db.regions[self._mock_db.regions['REGION_ID'] == region_id]['REGION_NAME'].values[0]
                report_lines.append(f"  {region_name}: ${revenue:,.2f}")
            
            avg_trans = self._mock_db.kpi_df[self._mock_db.kpi_df['KPI_NAME'] == 'AVG_TRANSACTION_VALUE']['KPI_VALUE'].mean()
            report_lines.append("")
            report_lines.append(f"Average Transaction Value: ${avg_trans:,.2f}")
            
            report_text = "\n".join(report_lines)
            report_file = self.summaries_path / f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            with open(report_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Generated text report: {report_file}")
            return report_text
        
        def mock_generate_insights(self):
            from datetime import datetime
            insights = "Demo Mode: Sample insights generated\n"
            insights += "Revenue trends are positive across all regions\n"
            insights += "Top customers show consistent growth patterns"
            
            insight_file = self.insights_path / f'insights_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            with open(insight_file, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("AUTOMATED INSIGHTS REPORT (DEMO MODE)\n")
                f.write("=" * 80 + "\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                f.write(insights)
            logger.info(f"Generated insight file: {insight_file}")
        
        ReportGenerator.generate_kpi_summary_csv = mock_generate_csv
        ReportGenerator.generate_text_report = mock_generate_text
        ReportGenerator.generate_insight_file = mock_generate_insights
        
        report_gen.generate_all_reports()
        
        logger.info("=" * 80)
        logger.info("DEMO MODE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"Charts saved to: reports/charts/")
        logger.info(f"Reports saved to: reports/summaries/")
        logger.info(f"Insights saved to: reports/insights/")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Demo mode failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    run_demo()

