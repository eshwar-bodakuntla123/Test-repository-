-- 👇 change this value for how many days of tables you want to keep
DECLARE expiry_days INT64 DEFAULT 1;

DECLARE project_id STRING DEFAULT "gatp-excellence";
DECLARE dataset_id STRING DEFAULT "analytics_501940433";

BEGIN
  FOR rec IN (
    SELECT table_name
    FROM `gatp-excellence.analytics_501940433.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE 'events_intraday_%'
      AND SAFE.PARSE_DATE('%Y%m%d', SUBSTR(table_name, LENGTH('events_intraday_') + 1))
          < DATE_SUB(CURRENT_DATE(), INTERVAL expiry_days DAY)
  )
  DO
    -- Build the DROP statement
    EXECUTE IMMEDIATE FORMAT(
      "DROP TABLE IF EXISTS `%s.%s.%s`",
      project_id, dataset_id, rec.table_name
    );

    -- Optional: log which table was dropped
    SELECT rec.table_name AS dropped_table;
  END FOR;
END;