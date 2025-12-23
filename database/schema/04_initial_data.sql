-- =====================================================
-- Sample Reference Data
-- =====================================================

-- Insert Sample Regions
INSERT INTO REGIONS (REGION_ID, REGION_NAME, REGION_CODE, COUNTRY) VALUES (SEQ_REGION_ID.NEXTVAL, 'North America', 'NA', 'USA');
INSERT INTO REGIONS (REGION_ID, REGION_NAME, REGION_CODE, COUNTRY) VALUES (SEQ_REGION_ID.NEXTVAL, 'Europe', 'EU', 'UK');
INSERT INTO REGIONS (REGION_ID, REGION_NAME, REGION_CODE, COUNTRY) VALUES (SEQ_REGION_ID.NEXTVAL, 'Asia Pacific', 'APAC', 'India');
INSERT INTO REGIONS (REGION_ID, REGION_NAME, REGION_CODE, COUNTRY) VALUES (SEQ_REGION_ID.NEXTVAL, 'Middle East', 'ME', 'UAE');

COMMIT;

