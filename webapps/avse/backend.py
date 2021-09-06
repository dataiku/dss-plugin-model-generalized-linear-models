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
from a_vs_e.ave_utils import get_ave_data

ave_data, target, weight = get_ave_data()

if weight==None:
    weight = 'weight'
    ave_data[weight] = 1
    
prediction = 'prediction'
weighted_target = 'weighted_target'
weighted_prediction = 'weighted_prediction'
ave_data['weighted_target'] = ave_data[target] * ave_data[weight]
ave_data['weighted_prediction'] = ave_data[prediction] * ave_data[weight]

excluded_columns = [target, prediction, weight, weighted_target, weighted_prediction, 'ClaimAmount']
feature_names = [c for c in ave_data.columns if c not in excluded_columns]

# bin numerical features
for c in feature_names:
    if is_numeric_dtype(ave_data[c].dtype):
        if len(ave_data[c].unique())>20:
            ave_data[c] = [str(x.left) + ', ' + str(x.right) for x in pd.cut(ave_data[c], bins=20)]

ave_grouped = {c: ave_data.groupby([c]).agg({weighted_target: 'sum', weighted_prediction: 'sum', weight: 'sum'}).reset_index() 
               for c in feature_names}
for c in ave_grouped:
    ave_grouped[c][weighted_target] = ave_grouped[c][weighted_target]/ave_grouped[c][weight]
    ave_grouped[c][weighted_prediction] = ave_grouped[c][weighted_prediction]/ave_grouped[c][weight]

app.config.external_stylesheets = [dbc.themes.BOOTSTRAP]

def feature_table():
    table = dash_table.DataTable(
        id="feature-table",
        columns=(
                [{'id': 'Feature', 'name': 'Feature'}]
             ),
        data=[{'Feature': f}
              for f in feature_names],
    style_header={'fontWeight': 'bold'},
    style_table={'height': '300px',
                 "overflowY": "scroll"},
    style_cell={'textAlign': 'left',
               'padding': '5px',
               'whiteSpace': 'normal',
               'height': 'auto'},
    sort_action="native",
    sort_mode="multi",
    page_action='none',
    editable=False)
    return table

feature_choice = dcc.RadioItems(
    id='feature-choice',
    options=[{'label': f, 'value': f}
              for f in feature_names],
    value=feature_names[0],
    labelStyle={'display': 'block'},
    style={"height": "100px",
           "width": "150px",
         "overflowY": "scroll"}

)  

app.layout = dbc.Container(
    [
        feature_choice,
        dcc.Graph(id="AvE"),
    ],
    fluid=True)


@app.callback(
    Output("AvE", "figure"),
    Input('feature-choice', 'value')
)
def make_graph(feature):
    data = ave_grouped[feature].dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=data[feature], y=data[weight],
                name='weight'),
                secondary_y=False)
    fig.add_trace(go.Scatter(x=data[feature], y=data[weighted_target],
                    mode='lines',
                    name='target'),
                    secondary_y=True)
    fig.add_trace(go.Scatter(x=data[feature], y=data[weighted_prediction],
                    mode='lines',
                    name='prediction'),
                    secondary_y=True)
    return fig