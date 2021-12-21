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

app.config.external_stylesheets = [dbc.themes.BOOTSTRAP, 'plugins/generalize-linear-models/webapps/avse/dss_style.css']

feature_choice = dcc.Dropdown(
    id='feature-choice',
    options=[{'label': f, 'value': f}
             for f in features],
    value=features[0], style={'display': 'inline-block', 'vertical-align': 'top', 'width': '60%',
                              'margin-bottom': '1em'}
)

app.layout = dbc.Row([
    dbc.Col([
        dbc.Container(
            [
                html.H4("Generalized Linear Model Analysis", style={'margin-top': '1em'}),
                html.H5("Model Metrics", style={'margin-top': '1em'}),
                dbc.Row([
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("BIC Score ", style={'textAlign': 'left'}),
                                    html.H5(f"{np.round(predictor._clf.fitted_model.bic, 2):,}",
                                            style={'textAlign': 'center'})

                                ]), style={'margin-bottom': '1em'}
                        )
                    ], md=4),

                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("AIC Score ", style={'textAlign': 'left'}),
                                    html.H5(f"{np.round(predictor._clf.fitted_model.aic, 2):,}",
                                            style={'textAlign': 'center'})

                                ]), style={'margin-bottom': '1em'}
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Deviance ", style={'textAlign': 'left'}),
                                    html.H5(f"{np.round(predictor._clf.fitted_model.deviance, 2):,}",
                                            style={'textAlign': 'center'})

                                ]), style={'margin-bottom': '1em'}
                        )
                    ], md=4)
                ]),

                html.H5("Variable Analysis", style={'margin-top': '1em'}),
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div([
                                html.H5("Select a Feature",
                                        style={'display': 'inline-block', 'vertical-align': 'centre', 'width': '20%',
                                               'margin-left': '1em', 'margin-bottom': '1em'}),
                                feature_choice
                            ]),
                            html.H5("Actual Vs Expected Graph", style={'margin-left': '1em', 'margin-bottom': '1em'}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Card(
                                        dcc.Graph(id="AvE")
                                    )
                                ], md=8),

                                dbc.Col([
                                    dbc.Card(
                                        html.P(
                                            "The base graph displays the target against the base prediction, which is the pure effect of the chosen variable. " +
                                            "Numerical variables are automatically binned. " +
                                            "The background bars represent the overall weight (number of observations x weight) of each bin. " +
                                            "The base prediction of each bin is the weighted prediction when all the variables except the chosen one are at their base value. " +
                                            "The base value of a variable is its modal value, meaning the most frequent one (the most frequent bin when numerical).",
                                            style={'margin-top': '1em', 'margin-bottom': '1em', 'margin-right': '1em',
                                                   'margin-left': '1em', 'fontSize': '13px', 'color': '#222222'}
                                        ),
                                        style={'box-shadow': '0px 0px 0px 0px',
                                               'background-color': 'rgba(135, 206, 250, 0.5)'})
                                ], md=4)
                            ]),

                            html.H5("Predicted Graph",
                                    style={'margin-top': '1em', 'margin-left': '1em', 'margin-bottom': '1em'}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Card(
                                        dcc.Graph(id="predicted_graph")
                                    )
                                ], md=8),

                                dbc.Col([
                                    dbc.Card(
                                        html.P(
                                            "The predicted graph compares target with prediction for each variable. " +
                                            "Numerical variables are automatically binned. " +
                                            "The background bars represent the overall weight (number of observations x weight) of each bin. " +
                                            "The two lines are the weighted target and prediction within each bin.",
                                            style={'margin-top': '1em', 'margin-bottom': '1em', 'margin-right': '1em',
                                                   'margin-left': '1em', 'fontSize': '13px', 'color': '#222222'}
                                            ),
                                        style={'box-shadow': '0px 0px 0px 0px',
                                               'background-color': 'rgba(135, 206, 250, 0.5)'}
                                    )
                                ], md=4)
                            ]),

                            html.H5("Ratio Graph",
                                    style={'margin-top': '1em', 'margin-left': '1em', 'margin-bottom': '1em'}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Card(
                                        dcc.Graph(id="ratio_graph")
                                    )
                                ], md=8),

                                dbc.Col([
                                    dbc.Card(
                                        html.P("The ratio graph uses the same data as the predicted graphs. " +
                                               "Instead of comparing expected and predicted side by side, " +
                                               "the predicted value is divided by the expected value for each bin.",
                                               style={'margin-top': '1em', 'margin-bottom': '1em',
                                                      'margin-right': '1em', 'margin-left': '1em', 'fontSize': '13px',
                                                      'color': '#222222'}
                                               ),
                                        style={'box-shadow': '0px 0px 0px 0px',
                                               'background-color': 'rgba(135, 206, 250, 0.5)'}
                                    )
                                ], md=4)
                            ]),

                        ]), style={'margin-bottom': '1em'}
                )
            ], fluid=True)
    ], md=11),
    dbc.Col([

    ], style={'background-color': '#f2f2f2'}, md=1)
])


@app.callback(
    Output('AvE', 'figure'),
    Input('feature-choice', 'value')
)
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


@app.callback(
    Output('predicted_graph', 'figure'),
    Input('feature-choice', 'value')
)
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


@app.callback(
    Output('ratio_graph', 'figure'),
    Input('feature-choice', 'value')
)
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