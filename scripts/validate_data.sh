#!/bin/bash

# Data Validation Wrapper Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

source venv/bin/activate

python -c "
from python.analytics.data_validator import DataValidator
from python.utils.logger import setup_logger

logger = setup_logger(__name__)
validator = DataValidator()
results = validator.validate_all()
print('Validation Results:')
for key, value in results.items():
    print(f'  {key}: {value}')
"

