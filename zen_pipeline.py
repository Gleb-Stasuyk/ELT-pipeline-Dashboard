#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import getopt
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go


# задаем данные для отрисовки
from sqlalchemy import create_engine 



if __name__ == "__main__":

    # Задаём входные параметры
    unixOptions = "sdt:edt"
    gnuOptions = ["start_dt=", "end_dt="]

    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:]  # excluding script name

    try:
        arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    start_dt = ''
    end_dt = ''
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-sdt", "--start_dt"):
            start_dt = currentValue
        elif currentArgument in ("-edt", "--end_dt"):
            end_dt = currentValue

    db_config = {'user': 'my_user',
                 'pwd': 'my_user_password',
                 'host': 'localhost',
                 'port': 5432,
                 'db': 'zen'}

    connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                             db_config['pwd'],
                                                             db_config['host'],
                                                             db_config['port'],
                                                             db_config['db'])
    engine = create_engine(connection_string)

    # Теперь выберем из таблицы только те строки,
    # которые были выпущены между start_dt и end_dt
    query = ''' SELECT event_id, age_segment, event, item_id, item_topic,
                    item_type, source_id, source_topic, source_type,
                    TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' as dt, user_id
                    FROM log_raw
                    WHERE TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
                '''.format(start_dt, end_dt)

    data_raw = pd.io.sql.read_sql(query, con=engine, index_col='event_id')


    columns_numeric = ['item_id', 'source_id', 'user_id']
    columns_datetime = ['dt']
    for column in columns_numeric: data_raw[column] = pd.to_numeric(data_raw[column], errors='coerce')
    for column in columns_datetime: data_raw[column] = pd.to_datetime(data_raw[column]).dt.round('min')


    #Sagg_games_year = data_raw.groupby('year_of_release').agg({'critic_score': 'mean'})
    dash_visits = data_raw.groupby(['item_topic', 'source_topic', 'age_segment', 'dt'])['user_id'].agg({'count'}).reset_index()
    dash_visits = dash_visits.rename(columns = {'count': 'visits'})
    dash_engagement = data_raw.groupby(['item_topic', 'age_segment', 'dt', 'event'])['user_id'].agg({'nunique'}).reset_index()
    dash_engagement = dash_engagement.rename(columns = {'nunique': 'unique_users'})
    

    
    #Удаляем старые записи между start_dt и end_dt
    query = '''DELETE FROM dash_visits 
                   WHERE dt BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
            '''.format(start_dt, end_dt)
    engine.execute(query)

    dash_visits.to_sql(name = 'dash_visits', con = engine, if_exists = 'append', index = False)
    
    query = '''DELETE FROM dash_engagement 
                   WHERE dt BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
            '''.format(start_dt, end_dt)
    engine.execute(query)

    dash_engagement.to_sql(name = 'dash_engagement', con = engine, if_exists = 'append', index = False)
    
    

 
    # берем значения из таблиц
    query = ''' SELECT *
                    FROM dash_visits
                    WHERE dt BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
                '''.format(start_dt, end_dt)

    dash_visits = pd.io.sql.read_sql(query, con=engine)
    
    
    query = ''' SELECT *
                    FROM dash_engagement
                    WHERE dt BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
                '''.format(start_dt, end_dt)

    dash_engagement = pd.io.sql.read_sql(query, con=engine)
    print('all done')