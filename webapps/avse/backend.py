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

sys.modules['generalized_linear_models'] = generalized_linear_models
from a_vs_e.actual_vs_predicted_utils import get_ave_grouped, get_original_model_handler

palette = '#BDD8ED', '#3075AE', '#4F934F'
ave_grouped = get_ave_grouped()
features = [k for k in ave_grouped.keys()]

model_handler = get_original_model_handler()
predictor = model_handler.get_predictor()

app.config.external_stylesheets = [dbc.themes.BOOTSTRAP]

feature_choice = dcc.Dropdown(
    id='feature-choice',
    options=[{'label': f, 'value': f}
             for f in features],
    value=features[0], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '62%','margin-top':'15px','margin-bottom':'15px'}
)

app.layout = dbc.Container(
    [
        html.H1("Generalized Linear Model Analysis", style={'margin-top':'15px'}),
        html.H6("The predicted tab show the blah vs blah"),
        html.H6("The base tab show the blah vs blah"),
        html.Div([
            dcc.Tabs(id="tabs", value='predicted', children=[
                dcc.Tab(label='Predicted', value='predicted'),
                dcc.Tab(label='Base', value='base'),
            ], style={'margin-right': '15px','margin-left': '15px'}),
            html.Div([
                html.H4("Select a Feature", style={'display': 'inline-block','vertical-align': 'center', 'width': '10%','margin-left': '15px','margin-top':'33px','margin-bottom':'15px'}),
                feature_choice
            ]),
            html.H4("Actual Vs Expected Graph",style={'margin-left': '15px','margin-bottom':'15px'}),
            dcc.Graph(id="AvE", style={'margin-right': '15px','margin-left': '15px','margin-top':'15px','margin-bottom':'15px'})
        ], style={'border-radius': '15px','box-shadow': '8px 8px 8px grey','background-color': '#f9f9f9',
                       'padding': '10px','margin-bottom': '50px','margin-top': '50px',}),


        html.Div([
            html.Div([
                html.H4("BIC Score ", style={'textAlign': 'left', 'marginBottom': '50px'}),
                html.H1(f"{np.round(predictor._clf.fitted_model.bic, 2):,}", style={'textAlign': 'center','margin-bottom': '50px'})

            ], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '32%',
                      'border-radius': '15px','box-shadow': '8px 8px 8px grey','background-color': '#f9f9f9',
                       'padding': '10px','margin-right': '30px'}),

            html.Div([
                html.H4("AIC Score ", style={'textAlign': 'left', 'marginBottom': '50px'}),
                html.H1(f"{np.round(predictor._clf.fitted_model.aic, 2):,}", style={'textAlign': 'center','margin-bottom': '50px'})

            ], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '32%',
                      'border-radius': '15px','box-shadow': '8px 8px 8px grey','background-color': '#f9f9f9',
                       'padding': '10px','margin-left': '15px','margin-right': '15px'}),

            html.Div([
                html.H4("Deviance ", style={'textAlign': 'left', 'marginBottom': '50px'}),
                html.H1(f"{np.round(predictor._clf.fitted_model.deviance, 2):,}", style={'textAlign': 'center','margin-bottom': '50px'})

            ], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '32%',
                      'border-radius': '15px','box-shadow': '8px 8px 8px grey','background-color': '#f9f9f9',
                       'padding': '10px','margin-left': '30px'}),

        ])

    ],
    fluid=True)


@app.callback(Output('tab-description', 'children'),
              Input('tabs', 'value'))
def news_scores(tab):
    if tab == 'predicted':
        return html.P("The predicted graph compares target with prediction for each variable. " +
                      "Numerical variables are automatically binned. " +
                      "The background bars represent the overall weight (number of observations x weight) of each bin. " +
                      "The two lines are the weighted target and prediction within each bin.")
    elif tab == 'base':
        return html.P(
            "The base graph displays the target against the base prediction, which is the pure effect of the chosen variable. " +
            "Numerical variables are automatically binned. " +
            "The background bars represent the overall weight (number of observations x weight) of each bin. " +
            "The base prediction of each bin is the weighted prediction when all the variables except the chosen one are at their base value. " +
            "The base value of a variable is its modal value, meaning the most frequent one (the most frequent bin when numerical).")


@app.callback(
    Output('AvE', 'figure'),
    Input('feature-choice', 'value'),
    Input('tabs', 'value')
)
def make_graph(feature, tab):
    if tab == 'predicted':
        return predicted_graph(feature)
    elif tab == 'base':
        return base_graph(feature)
    elif tab == 'ratio':
        return ratio_graph(feature)


def base_graph(feature):
    data = ave_grouped[feature].dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=data[feature], y=data['weight'],
                         name='weight',
                         marker=dict(color=palette[0])),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_target'],
                             mode='lines',
                             name='target',
                             line=dict(color=palette[1])),
                  secondary_y=True)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_base'],
                             mode='lines',
                             name='base',
                             line=dict(color=palette[2])),
                  secondary_y=True)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.layout.yaxis.gridcolor = '#D7DBDE'
    return fig


def predicted_graph(feature):
    data = ave_grouped[feature].dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=data[feature], y=data['weight'],
                         name='weight',
                         marker=dict(color=palette[0])),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_target'],
                             mode='lines',
                             name='target',
                             line=dict(color=palette[1])),
                  secondary_y=True)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_prediction'],
                             mode='lines',
                             name='prediction',
                             line=dict(color=palette[2])),
                  secondary_y=True)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.layout.yaxis.gridcolor = '#D7DBDE'
    return fig


def ratio_graph(feature):
    data = ave_grouped[feature].dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=data[feature], y=data['weight'],
                         name='weight',
                         marker=dict(color=palette[0])),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_prediction']/data['weighted_target'],
                             mode='lines',
                             name='actual/expected',
                             line=dict(color=palette[1])),
                  secondary_y=True)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.layout.yaxis.gridcolor = '#D7DBDE'
    return fig