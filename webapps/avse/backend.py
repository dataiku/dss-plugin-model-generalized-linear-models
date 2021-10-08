from dataiku.customwebapp import *
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from pandas.api.types import is_numeric_dtype
import dataiku
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
import generalized_linear_models
sys.modules['generalized_linear_models']=generalized_linear_models
from a_vs_e.actual_vs_predicted_utils import get_ave_grouped

ave_grouped = get_ave_grouped()
features = [k for k in ave_grouped.keys()]

app.config.external_stylesheets = [dbc.themes.BOOTSTRAP]

feature_choice = dcc.RadioItems(
    id='feature-choice',
    options=[{'label': f, 'value': f}
              for f in features],
    value=features[0],
    labelStyle={'display': 'block'},
    style={"height": "100px",
           "width": "150px",
         "overflowY": "scroll"}

)  

app.layout = dbc.Container(
    [
        html.Div([
            dcc.Tabs(id="tabs", value='predicted', children=[
                dcc.Tab(label='Predicted', value='predicted'),
                dcc.Tab(label='Base', value='base'),
            ]),
            feature_choice,
            dcc.Graph(id="AvE")
        ])
    ],
    fluid=True)


@app.callback(
    Output('AvE', 'figure'),
    Input('feature-choice', 'value'),
    Input('tabs', 'value')
)
def make_graph(feature, tab):
    print(feature)
    if tab == 'predicted':
        return predicted_graph(feature)
    elif tab == 'base':
        return base_graph(feature)
        
def base_graph(feature):
    data = ave_grouped[feature].dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=data[feature], y=data['weight'],
                name='weight'),
                secondary_y=False)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_target'],
                    mode='lines',
                    name='target'),
                    secondary_y=True)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_base'],
                    mode='lines',
                    name='base'),
                    secondary_y=True)
    return fig
    
def predicted_graph(feature):
    data = ave_grouped[feature].dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=data[feature], y=data['weight'],
                name='weight'),
                secondary_y=False)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_target'],
                    mode='lines',
                    name='target'),
                    secondary_y=True)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_prediction'],
                    mode='lines',
                    name='prediction'),
                    secondary_y=True)
    return fig