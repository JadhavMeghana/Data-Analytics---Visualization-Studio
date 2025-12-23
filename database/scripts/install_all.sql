-- =====================================================
-- Master Installation Script
-- Run this script to install all database objects
-- =====================================================

-- Set SQL*Plus settings
SET ECHO ON
SET FEEDBACK ON
SET VERIFY OFF

-- Run schema scripts
@@schema/01_create_tables.sql
@@schema/02_create_indexes.sql
@@schema/03_create_sequences.sql
@@schema/04_initial_data.sql

-- Run procedure scripts
@@procedures/pkg_error_logging.pks
@@procedures/pkg_error_logging.pkb
@@procedures/pkg_data_validation.pks
@@procedures/pkg_data_validation.pkb
@@procedures/pkg_kpi_calculations.pks
@@procedures/pkg_kpi_calculations.pkb

PROMPT =====================================================
PROMPT Installation Complete!
PROMPT =====================================================

