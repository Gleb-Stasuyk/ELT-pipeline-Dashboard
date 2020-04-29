#!/usr/bin/python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

from datetime import datetime

import pandas as pd

# задаем данные для отрисовки
from sqlalchemy import create_engine 

# пример подключения к базе данных для Postresql
db_config = {'user': 'my_user',
             'pwd': 'my_user_password',
             'host': 'localhost',
             'port': 5432,
             'db': 'zen'}
engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                            db_config['pwd'],
                                                            db_config['host'],
                                                            db_config['port'],
                                                            db_config['db']))

# получаем сырые данные

query = '''
            select *
            from dash_visits 
        '''
dash_visits = pd.io.sql.read_sql(query, con = engine)

query = '''
            select *
            from dash_engagement 
        '''
dash_engagement = pd.io.sql.read_sql(query, con = engine)




note = '''
          Анализ пользовательского взаимодействия с карточками статей
       '''

# задаём лейаут
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,compress=False)
app.layout = html.Div(children=[  
    
    # формируем html
    html.H1(children = 'Дашборд для Яндекс Дзен'),

    html.Br(),

    # пояснения
    html.Label(note),

    html.Br(),      

    # Input
    
    html.Div([
        html.Div([
            
            html.Br(),
            
            html.Label('История визитов:'),
                dcc.DatePickerRange(
                    start_date = dash_visits['dt'].min(),
                    end_date = dash_visits['dt'].max(),
                    display_format = 'YYYY-MM-DD',
                    id = 'year-selector',       
                ),
                
            html.Label('Темы:'),
                dcc.Dropdown(
                    id = 'item-topic-dropdown',
                    options = [{'label': x, 'value': x} for x in dash_visits['item_topic'].unique()],
                    value = dash_visits['item_topic'].unique(),
                    multi = True
                ),    
            ], className = 'six columns'),      

                

        html.Div([
        
            html.Br(),
            
            html.Label('Возраст:'),
                dcc.Dropdown(
                    id = 'age-dropdown',
                    options = [{'label': x, 'value': x} for x in dash_visits['age_segment'].unique()],
                    value = dash_visits['age_segment'].unique(),
                    multi = True
                ),    
            ], className = 'six columns'), 
            
                    ], className = 'row'),  
    
    html.Br(),  
            
            
    
    # Output
    
    html.Div([
        html.Div([
            
            html.Br(),
            
            # график выпуска игр по годам и жанрам
            html.Label('График истории событий по темам:'),    

            dcc.Graph(
                style = {'height': '50vw'},              
                id = 'history-absolute-visits'
            ),  

        ], className = 'six columns'),            

        html.Div([

            html.Br(),
            
            # график выпуска игр по платформам
            html.Label('Разбивка событий по темам:'),

            dcc.Graph(
                style = {'height': '25vw'},
                id = 'pie-visits'
            ),  

            # график выпуска игр по платформам
            html.Label('График средней глубины взаимодействия:'),

            dcc.Graph(
                style = {'height': '25vw'},              
                id = 'engagement-graph'
            ),                           

        ], className = 'six columns'),

    ], className = 'row'),  
 
])


#описываем логику дашборда
@app.callback(
    [Output('history-absolute-visits', 'figure'),
     Output('pie-visits', 'figure'),
     Output('engagement-graph', 'figure'),
    ],
    [
     Input('item-topic-dropdown', 'value'),
     Input('age-dropdown', 'value'),     
     Input('year-selector', 'start_date'),
     Input('year-selector', 'end_date'),

    ])
def update_figures(selected_item_topics, selected_ages, start_date, end_date):
    
    dash_visits_filtered = dash_visits.query('item_topic.isin(@selected_item_topics) and dt >= @start_date and dt <= @end_date and age_segment.isin(@selected_ages)')
    dash_engagement_filtered = dash_engagement.query('item_topic.isin(@selected_item_topics) and dt >= @start_date and dt <= @end_date and age_segment.isin(@selected_ages)')
    
    
    visits_history = dash_visits_filtered.groupby(['item_topic', 'dt']).agg({'visits':'sum'}).reset_index()
    
    history_absolute_visits_data = []
    
    for item_topic in visits_history.sort_values('visits', ascending=True)['item_topic'].unique():
        #current_data = visits_history[visits_history['item_topic'] == current_name]
        #visits_history = visits_history.sort_values('visits', ascending=False)
        history_absolute_visits_data += [go.Scatter(x = visits_history.query('item_topic == @item_topic')['dt'],
                                              y = visits_history.query('item_topic == @item_topic')['visits'],
                                              mode = 'lines',
                                              stackgroup = 'one',
                                              line = {'width': 1},
                                              name = item_topic)]  
    
    
    
    
    
    
    
    
    
    source_topic_visits = (dash_visits_filtered.groupby(['source_topic'])
                                   .agg({'visits': 'sum'})
                                   .reset_index())
    # все платформы с малым количеством игр помещаем в одну категорию
    source_topic_visits['percent'] = source_topic_visits['visits'] / source_topic_visits['visits'].sum()
    source_topic_visits.loc[source_topic_visits['percent'] < 0.01, 'source_topic'] = 'Другие'
    # и ещё раз группируем
    report = (source_topic_visits.groupby(['source_topic'])
                                          .agg({'visits': 'sum'})
                                          .reset_index())

    pie_visits_data = [go.Pie(labels = report['source_topic'],
                             values = report['visits'],
                             name = 'platfroms')]
    
       
            
      
    engagement_graph = dash_engagement_filtered.groupby('event').agg({'unique_users':['mean']}).reset_index()
    engagement_graph.columns = engagement_graph.columns.droplevel(0)
    #engagement_graph['avg_unique_users'] = engagement_graph['sum'] / engagement_graph['count']
    engagement_graph.columns = ['event', 'avg_unique_users'] 
    engagement_graph = engagement_graph.sort_values(by='avg_unique_users', ascending=False)
    engagement_graph['avg_unique_users'] = engagement_graph['avg_unique_users'] / engagement_graph['avg_unique_users'].max()
    engagement_graph_data = [go.Bar(x = engagement_graph['event'],
                             y = engagement_graph['avg_unique_users'],
                             text = engagement_graph['avg_unique_users'].round(2), textposition='auto',
                             name = 'platfroms')]
            
            
    return (
           #history-absolute-visits
           #stacked area
            {
                'data': history_absolute_visits_data,
                'layout': go.Layout(xaxis = {'title': 'Год'},
                                    yaxis = {'title': 'Количество просмотров'})
             },  
           #pie-visits
            {
                'data': pie_visits_data,
             },           
           #engagement-graph
           # bar
            {
                'data': engagement_graph_data,
             }, 
        )


if __name__ == '__main__':
    app.run_server(debug = True, host='0.0.0.0')
