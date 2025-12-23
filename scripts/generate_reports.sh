#!/bin/bash

# Report Generation Wrapper Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

source venv/bin/activate

python -c "
from python.visualization.chart_generator import ChartGenerator
from python.visualization.report_generator import ReportGenerator

print('Generating charts...')
chart_gen = ChartGenerator()
chart_gen.generate_all_charts()

print('Generating reports...')
report_gen = ReportGenerator()
report_gen.generate_all_reports()

print('Done!')
"

