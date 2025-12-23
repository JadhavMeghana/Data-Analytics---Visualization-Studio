"""
Flask Web Application - Frontend for Enterprise Sales Analytics
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.utils.logger import setup_logger
from python.utils.config_loader import load_config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enterprise-sales-analytics-2024'
app.config['UPLOAD_FOLDER'] = 'data/input'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

logger = setup_logger(__name__, 'logs/web_app.log')


def get_reports_data():
    """Get available reports and charts"""
    config = load_config()
    charts_path = Path(config['paths']['reports_charts'])
    summaries_path = Path(config['paths']['reports_summaries'])
    insights_path = Path(config['paths']['reports_insights'])
    
    charts = []
    if charts_path.exists():
        charts = [f.name for f in charts_path.glob('*.png')] + [f.name for f in charts_path.glob('*.html')]
    
    reports = []
    if summaries_path.exists():
        reports = [f.name for f in summaries_path.glob('*.txt')] + [f.name for f in summaries_path.glob('*.csv')]
    
    insights = []
    if insights_path.exists():
        insights = [f.name for f in insights_path.glob('*.txt')]
    
    return charts, reports, insights


def get_latest_report():
    """Get the latest text report content"""
    config = load_config()
    summaries_path = Path(config['paths']['reports_summaries'])
    
    if summaries_path.exists():
        txt_files = list(summaries_path.glob('report_*.txt'))
        if txt_files:
            latest = max(txt_files, key=lambda p: p.stat().st_mtime)
            with open(latest, 'r') as f:
                return f.read()
    return "No reports available. Please run the analytics pipeline first."


def get_kpi_summary():
    """Get KPI summary data"""
    config = load_config()
    summaries_path = Path(config['paths']['reports_summaries'])
    
    if summaries_path.exists():
        csv_files = list(summaries_path.glob('kpi_summary_*.csv'))
        if csv_files:
            latest = max(csv_files, key=lambda p: p.stat().st_mtime)
            df = pd.read_csv(latest)
            return df.to_dict('records')
    return []


@app.route('/')
def index():
    """Main dashboard page"""
    charts, reports, insights = get_reports_data()
    latest_report = get_latest_report()
    kpi_data = get_kpi_summary()
    
    # Calculate summary statistics
    summary_stats = {
        'total_charts': len([c for c in charts if c.endswith('.png')]),
        'interactive_dashboards': len([c for c in charts if c.endswith('.html')]),
        'reports': len(reports),
        'insights': len(insights)
    }
    
    return render_template('index.html', 
                         charts=charts[:5],  # Show latest 5
                         reports=reports[:5],
                         insights=insights[:5],
                         latest_report=latest_report,
                         kpi_data=kpi_data[:10],  # Show latest 10 KPIs
                         summary_stats=summary_stats)


@app.route('/dashboard')
def dashboard():
    """Interactive dashboard page"""
    charts, _, _ = get_reports_data()
    dashboard_file = None
    
    # Find interactive dashboard
    config = load_config()
    charts_path = Path(config['paths']['reports_charts'])
    dashboard_path = charts_path / 'interactive_dashboard.html'
    
    if dashboard_path.exists():
        dashboard_file = 'interactive_dashboard.html'
    
    return render_template('dashboard.html', dashboard_file=dashboard_file)


@app.route('/charts')
def charts():
    """Charts gallery page"""
    charts, _, _ = get_reports_data()
    config = load_config()
    charts_path = Path(config['paths']['reports_charts'])
    
    chart_list = []
    for chart in charts:
        chart_path = charts_path / chart
        if chart_path.exists():
            stat = chart_path.stat()
            chart_list.append({
                'name': chart,
                'size': f"{stat.st_size / 1024:.1f} KB",
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'Interactive Dashboard' if chart.endswith('.html') else 'Chart'
            })
    
    return render_template('charts.html', charts=chart_list)


@app.route('/reports')
def reports():
    """Reports page"""
    _, reports, insights = get_reports_data()
    config = load_config()
    summaries_path = Path(config['paths']['reports_summaries'])
    insights_path = Path(config['paths']['reports_insights'])
    
    report_list = []
    for report in reports:
        report_path = summaries_path / report
        if report_path.exists():
            stat = report_path.stat()
            report_list.append({
                'name': report,
                'size': f"{stat.st_size / 1024:.1f} KB",
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'CSV' if report.endswith('.csv') else 'Text Report'
            })
    
    insight_list = []
    for insight in insights:
        insight_path = insights_path / insight
        if insight_path.exists():
            stat = insight_path.stat()
            insight_list.append({
                'name': insight,
                'size': f"{stat.st_size / 1024:.1f} KB",
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return render_template('reports.html', reports=report_list, insights=insight_list)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """File upload page"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.csv'):
            filename = file.filename
            filepath = Path(app.config['UPLOAD_FOLDER']) / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            file.save(str(filepath))
            
            logger.info(f"File uploaded: {filename}")
            return jsonify({
                'success': True,
                'message': f'File {filename} uploaded successfully!',
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400
    
    return render_template('upload.html')


@app.route('/view_chart/<filename>')
def view_chart(filename):
    """View a specific chart"""
    config = load_config()
    charts_path = Path(config['paths']['reports_charts'])
    chart_path = charts_path / filename
    
    if chart_path.exists():
        return send_file(str(chart_path))
    return "Chart not found", 404


@app.route('/view_report/<filename>')
def view_report(filename):
    """View a specific report"""
    config = load_config()
    summaries_path = Path(config['paths']['reports_summaries'])
    report_path = summaries_path / filename
    
    if report_path.exists():
        if filename.endswith('.csv'):
            df = pd.read_csv(report_path)
            return render_template('view_csv.html', 
                                 filename=filename,
                                 data=df.to_dict('records'),
                                 columns=df.columns.tolist())
        else:
            with open(report_path, 'r') as f:
                content = f.read()
            return render_template('view_report.html', 
                                 filename=filename,
                                 content=content)
    return "Report not found", 404


@app.route('/view_insight/<filename>')
def view_insight(filename):
    """View a specific insight file"""
    config = load_config()
    insights_path = Path(config['paths']['reports_insights'])
    insight_path = insights_path / filename
    
    if insight_path.exists():
        with open(insight_path, 'r') as f:
            content = f.read()
        return render_template('view_report.html', 
                             filename=filename,
                             content=content)
    return "Insight file not found", 404


@app.route('/api/kpis')
def api_kpis():
    """API endpoint for KPI data"""
    kpi_data = get_kpi_summary()
    return jsonify(kpi_data)


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    charts, reports, insights = get_reports_data()
    return jsonify({
        'charts': len([c for c in charts if c.endswith('.png')]),
        'dashboards': len([c for c in charts if c.endswith('.html')]),
        'reports': len(reports),
        'insights': len(insights)
    })


@app.route('/run_demo')
def run_demo():
    """Trigger demo mode execution"""
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, 'python/demo_mode.py'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Demo mode executed successfully!',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Demo mode execution failed',
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Create static directory if it doesn't exist
    static_dir = Path(__file__).parent / 'static'
    static_dir.mkdir(exist_ok=True)
    
    logger.info("Starting Flask web application...")
    app.run(debug=True, host='0.0.0.0', port=5000)

