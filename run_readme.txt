Instructions for launching pfpline and dashboard:

1) Restore db name.dump
cp name.dump /tmp
CREATE_DB name;
CREATE USER my_user WITH ENCRYPTED PASSWORD 'my_user_password';
GRANT ALL PRIVILEGES ON DATABASE zen TO my_user;
PG_RESTORE -d name /tmp/name.dump
GRANT USAGE, SELECT ON SEQUENCE dash_visits_record_id_seq TO my_user;
GRANT USAGE, SELECT ON SEQUENCE dash_engagement_record_id_seq TO my_user;

2) mkdir /home/user_name/logs
3) crontab -e
4) Add a line at the end of the file: 0 0 * * */1 python -u -W ignore /home/user_name/pipeline.py  --start_dt='2020-01-1 00:00:00' --end_dt='2020-01-07 00:00:00' >> /home/user_name/logs/script_zen_pipeline.log 2>&1
5) python3 zen_pipeline.py --start_dt='2020-01-1 00:00:00' --end_dt='2020-01-07 00:00:00'
6) python3 dash.py
7) localhost:8050
