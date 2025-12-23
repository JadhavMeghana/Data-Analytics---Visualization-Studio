#!/bin/bash

# =====================================================
# Enterprise Sales Analytics Pipeline Runner
# =====================================================

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
PYTHON_ENV="${PYTHON_ENV:-venv}"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/pipeline_$(date +%Y%m%d_%H%M%S).log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if Python virtual environment exists
check_venv() {
    if [ ! -d "$PROJECT_ROOT/$PYTHON_ENV" ]; then
        log "ERROR: Python virtual environment not found at $PROJECT_ROOT/$PYTHON_ENV"
        log "Please create it using: python -m venv $PYTHON_ENV"
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    source "$PROJECT_ROOT/$PYTHON_ENV/bin/activate"
    log "Activated Python virtual environment"
}

# Function to check Oracle connection
check_oracle() {
    log "Checking Oracle database connection..."
    python -c "
from python.data_loader.oracle_connector import OracleConnector
try:
    with OracleConnector() as db:
        print('Oracle connection successful')
except Exception as e:
    print(f'Oracle connection failed: {e}')
    exit(1)
" 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        log "ERROR: Oracle database connection failed"
        exit 1
    fi
}

# Main execution
main() {
    log "=========================================="
    log "Starting Enterprise Sales Analytics Pipeline"
    log "=========================================="
    
    cd "$PROJECT_ROOT"
    
    # Check virtual environment
    check_venv
    
    # Activate virtual environment
    activate_venv
    
    # Check Oracle connection
    check_oracle
    
    # Run Python pipeline
    CSV_FILE="${1:-}"
    if [ -n "$CSV_FILE" ]; then
        log "Running pipeline with CSV file: $CSV_FILE"
        python python/main.py "$CSV_FILE" 2>&1 | tee -a "$LOG_FILE"
    else
        log "Running pipeline without data load (KPI calculation and reporting only)"
        python python/main.py 2>&1 | tee -a "$LOG_FILE"
    fi
    
    EXIT_CODE=${PIPESTATUS[0]}
    
    if [ $EXIT_CODE -eq 0 ]; then
        log "=========================================="
        log "Pipeline completed successfully!"
        log "=========================================="
    else
        log "=========================================="
        log "Pipeline failed with exit code: $EXIT_CODE"
        log "=========================================="
    fi
    
    exit $EXIT_CODE
}

# Run main function
main "$@"

