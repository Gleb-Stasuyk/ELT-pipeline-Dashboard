Инструкция по запуску:

1) Резвернуть zen_tmp.dump
cp zen.dump /tmp
create_db zen;
CREATE USER my_user WITH ENCRYPTED PASSWORD 'my_user_password';
GRANT ALL PRIVILEGES ON DATABASE zen TO my_user;
pg_restore -d zen /tmp/zen.dump
GRANT USAGE, SELECT ON SEQUENCE dash_visits_record_id_seq TO my_user;
GRANT USAGE, SELECT ON SEQUENCE dash_engagement_record_id_seq TO my_user;

2) mkdir /home/ИМЯ_ВАШЕГО_ПОЛЬЗОВАТЕЛЯ/logs
3) crontab -e
4) В конце файла добавьте строку: 0 0 * * */1 python -u -W ignore /home/ИМЯ_ВАШЕГО_ПОЛЬЗОВАТЕЛЯ/zen_pipeline.py  --start_dt='2019-09-24 18:00:00' --end_dt='2019-09-24 19:00:00' >> /home/ИМЯ_ВАШЕГО_ПОЛЬЗОВАТЕЛЯ/logs/script_zen_pipeline.log 2>&1
5) Запустить пайплайн python3 zen_pipeline.py --start_dt='2019-09-24 18:00:00' --end_dt='2019-09-24 19:00:00' (или дождаться полночи)
6) Запустить дашборд, python3 dash.py
7) Дашборд находится на :8050 порту вашей виртуальной машины