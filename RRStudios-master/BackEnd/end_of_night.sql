USE sql8162831;

INSERT INTO HISTORICAL_DATA (bar_id, time_in, time_out, day_of_week)
SELECT bar_id, time_in, time_out, day_of_week FROM REPORTS
where time_out IS NOT NULL;
TRUNCATE TABLE REPORTS;
commit;
