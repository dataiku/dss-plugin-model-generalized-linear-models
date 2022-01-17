from dataiku.customwebapp import *
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from glm_summary.graph_utils import get_ave_grouped
from glm_summary.dku_utils import get_ave_data, get_original_model_handler
from shutil import copytree

palette = '#D5D9D9', '#3075AE', '#4F934F'
ave_data, target, weight, class_map = get_ave_data()
ave_grouped = get_ave_grouped(ave_data, target, weight, class_map)
features = [k for k in ave_grouped.keys()]

model_handler = get_original_model_handler()
predictor = model_handler.get_predictor()
if not hasattr(predictor._clf, 'fitted_model'):
    raise ValueError('GLM Summary is only available for GLMs')

FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

webapp_plugin_assets = os.path.join(
    get_webapp_resource(), "../webapps/avse/assets"
)
dash_webapp_assets = app.config.assets_folder
print(
    f"Copying Webapp assets from directory '{webapp_plugin_assets}' into directory '{dash_webapp_assets}'"
)
copytree(webapp_plugin_assets, dash_webapp_assets)

app.config.external_stylesheets = ['dss_style.css', dbc.themes.BOOTSTRAP, FA]

feature_choice = dcc.Dropdown(
    id='feature-choice',
    options=[{'label': f, 'value': f}
             for f in features],
    value=features[0], style={'display': 'inline-block', 'width': '60%',
                              'margin-bottom': '1em'}
)

app.layout = dbc.Row([
    dbc.Col([
        dbc.Container(
            [
                html.H3("Generalized Linear Model Analysis"),
                html.Hr(),
                html.H4("Model Metrics", style={'margin-left': '1em'}),
                dbc.Row([
                    dbc.Col([
                        html.Table(
                            [html.Tr([
                                html.Td(["Bayesian Information Criterion (BIC) ",
                                         html.I(className="fa fa-question-circle mr-2",
                                                title="Criterion for model selection, models with lower BIC are generally preferred")]),
                                html.Th(f"{np.round(predictor._clf.fitted_model.bic, 2):,}")
                            ]),
                                html.Tr([
                                    html.Td(["Akaike Information Criterion (AIC) ",
                                             html.I(className="fa fa-question-circle mr-2",
                                                    title="Criterion for model selection, models with lower AIC are generally preferred")]),
                                    html.Th(f"{np.round(predictor._clf.fitted_model.aic, 2):,}")
                                ]),
                                html.Tr([
                                    html.Td(["Deviance ",
                                             html.I(className="fa fa-question-circle mr-2",
                                                    title="Measure of the error, using the likelihood function")]),
                                    html.Th(f"{np.round(predictor._clf.fitted_model.deviance, 2):,}")
                                ])
                            ],
                            className="detailed-metrics-table")
                    ], md=8),
                    dbc.Col([
                        html.Div([
                            dcc.Markdown('''
                            [BIC](https://en.wikipedia.org/wiki/Bayesian_information_criterion), 
                            [AIC](https://en.wikipedia.org/wiki/Akaike_information_criterion) and [
                            Deviance](https://en.wikipedia.org/wiki/Deviance_(statistics)) are metrics built as follows, with L the fitted likelihood and L_s the saturated likelihood: 
                            '''),
                        html.Code("BIC = nb_feature * ln(nb_observation) - 2 ln(L)"),
                        html.Br(),
                        html.Code("AIC = 2 * nb_feature - 2 ln(L)"),
                        html.Br(),
                        html.Code("Deviance = 2 * (ln(L_s) - ln(L))")
                            ], style={'display': 'block'}, className="explanation")
                    ], md=4)

                ]),
                html.Hr(),
                html.H4("Variable Analysis", style={'margin-left': '1em'}),
                dbc.Row([
                    dbc.Col(html.Div(), md=2),
                    dbc.Col(
                        html.H5("Select a Feature",
                                style={'display': 'inline-block', 'vertical-align': 'bottom',
                                       'margin-top': '0.5em'}),
                        md=2),
                    dbc.Col(feature_choice, md=8)
                ]),
                dbc.Row(
                    dbc.Col(
                        html.H5("Base Graph", style={'text-align': 'center', 'margin-left': '1em'}), md=8)
                ),

                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="AvE", style={'height': '50vh'})
                    ], md=8),

                    dbc.Col([
                        html.P(
                            "A base graph shows the pure dependence of the predicted response and the actual response on a single feature. The x axis displays the value "
                            "of the selected feature, while the y axis displays the base prediction along with the actual response. The base prediction of each bin is the weighted "
                            "prediction when all the variables except the chosen one are at their base value. " +
                            "The base value of a variable is its modal value, meaning the most frequent "
                            "one (the most frequent bin when numerical).",
                            className="explanation")
                    ], md=4)
                ]),

                dbc.Row(
                    dbc.Col(
                        html.H5("Predicted Graph", style={'text-align': 'center', 'margin-left': '1em'}), md=8)
                ),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="predicted_graph", style={'height': '50vh'})
                    ], md=8),

                    dbc.Col([
                        html.P(
                            "A predicted graph shows the value of the predicted and the actual response on a single "
                            "feature. The x axis displays the value "
                            "of the selected feature, while the y axis displays the weighted prediction and the "
                            "weighted actual response.",
                            className="explanation")
                    ], md=4)
                ]),

                dbc.Row(
                    dbc.Col(
                        html.H5("Ratio Graph", style={'text-align': 'center', 'margin-left': '1em'}), md=8)
                ),

                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="ratio_graph", style={'height': '50vh'})
                    ], md=8),

                    dbc.Col([
                        html.P("The ratio graph uses the same data as the predicted graph. " +
                               "Instead of comparing expected and predicted side by side, " +
                               "the predicted value is divided by the expected value for each bin.",
                               className="explanation")
                    ], md=4)
                ]),
            ], fluid=True)
    ], md=12),
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
    fig.layout.margin.t = 10
    fig.update_xaxes(title=feature)
    fig.update_yaxes(title='weight', secondary_y=False)
    fig.update_yaxes(title=target, secondary_y=True)
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
    fig.layout.margin.t = 10
    fig.update_xaxes(title=feature)
    fig.update_yaxes(title='weight', secondary_y=False)
    fig.update_yaxes(title=target, secondary_y=True)
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
    fig.layout.margin.t = 10
    fig.update_xaxes(title=feature)
    fig.update_yaxes(title='weight', secondary_y=False)
    fig.update_yaxes(title=target, secondary_y=True)
    return fig
