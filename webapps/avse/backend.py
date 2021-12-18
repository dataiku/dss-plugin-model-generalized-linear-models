from dataiku.customwebapp import *
import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash import dash_table
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
    value=features[0], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '64%',
                              'margin-top': '1em',
                              'margin-bottom': '1em'}
)

app.layout = dbc.Container(
    [
        html.H1("Generalized Linear Model Analysis", style={'margin-top': '1em'}),
        # html.Div([
        dbc.Card(
            dbc.CardBody(
                [
                    dcc.Tabs(id="tabs", value='predicted', children=[
                        dcc.Tab(label='Predicted', value='predicted'),
                        dcc.Tab(label='Base', value='base'),
                        dcc.Tab(label='Ratio', value='ratio'),
                    ], style={'margin-right': '1em', 'margin-left': '1em'}),
                    html.Div([
                        html.H4("Select a Feature",
                                style={'display': 'inline-block', 'vertical-align': 'center', 'width': '10%',
                                       'margin-left': '1em', 'margin-top': '1em', 'margin-bottom': '1em'}),
                        feature_choice
                    ]),
                    html.H4("Actual Vs Expected Graph", style={'margin-left': '1em', 'margin-bottom': '1em'}),
                    dbc.Container(id='tab-description'),
                    dcc.Graph(id="AvE", style={'margin-right': '1em', 'margin-left': '1em', 'margin-top': '1em',
                                               'margin-bottom': '1em'})
                ]), style={'margin-bottom': '1em'}
        ),

        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4("BIC Score ", style={'textAlign': 'left', 'marginBottom': '2em'}),
                            html.H1(f"{np.round(predictor._clf.fitted_model.bic, 2):,}",
                                    style={'textAlign': 'center', 'margin-bottom': '1em'})

                        ]), style={'margin-bottom': '1em'}
                )
            ], md=4),

            dbc.Col([
                dbc.Card(
                    dbc.CardBody(
                        [
                html.H4("AIC Score ", style={'textAlign': 'left', 'marginBottom': '2em'}),
                html.H1(f"{np.round(predictor._clf.fitted_model.aic, 2):,}",
                        style={'textAlign': 'center', 'margin-bottom': '1em'})

            ]), style={'margin-bottom': '1em'}
                )
                ], md=4),
        dbc.Col([
            dbc.Card(
                    dbc.CardBody(
                        [
                html.H4("Deviance ", style={'textAlign': 'left', 'marginBottom': '2em'}),
                html.H1(f"{np.round(predictor._clf.fitted_model.deviance, 2):,}",
                        style={'textAlign': 'center', 'margin-bottom': '1em'})

            ]), style={'margin-bottom': '1em'}
            )
        ], md=4)
    ])
], fluid=True)


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
    elif tab == 'ratio':
        return html.P("The ratio graph uses the same data as the predicted graphs. " +
                      "Instead of comparing expected and predicted side by side, " +
                      "the predicted value is divided by the expected value for each bin.")


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
    fig.add_trace(go.Scatter(x=data[feature], y=data['weighted_prediction'] / data['weighted_target'],
                             mode='lines',
                             name='actual/expected',
                             line=dict(color=palette[1])),
                  secondary_y=True)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.layout.yaxis.gridcolor = '#D7DBDE'
    return fig
