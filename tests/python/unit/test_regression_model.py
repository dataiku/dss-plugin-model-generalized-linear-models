from generalized_linear_models.dku_glm import RegressionGLM
import statsmodels.api as sm
import pytest
from testing_utils import testing_dict
import numpy as np
import pandas as pd
from sklearn import datasets

def test_link_function():
    expected = [
        sm.families.links.log(),
        sm.families.links.identity(),
        sm.families.links.inverse_power(),
        sm.families.links.inverse_squared(),
        sm.families.links.log(),
        sm.families.links.cloglog(),
        sm.families.links.Power(1),
        type(sm.families.Binomial()),
        type(sm.families.links.log())
    ]

    actual = []
    breast_cancer = datasets.load_breast_cancer()
    X, y = breast_cancer.data, breast_cancer.target

    for test in testing_dict:
        test_params = testing_dict[test]
        regression_model = RegressionGLM(
            penalty=0.0,
            offset_mode='BASIC',
            family_name=test_params['family_name'],
            binomial_link=test_params['binomial_link'],
            gamma_link=test_params['gamma_link'],
            gaussian_link=test_params['gaussian_link'],
            inverse_gaussian_link=test_params['inverse_gaussian_link'],
            poisson_link=test_params['poisson_link'],
            negative_binomial_link=test_params['negative_binomial_link'],
            tweedie_link=test_params['tweedie_link'],
            alpha=1,
            power=1,
            var_power=1)
        regression_model.assign_family()
        actual.append(regression_model.get_link_function())

    for act, exp in zip(actual, expected):
        assert type(act) == type(exp)


def test_regression():
    data = sm.datasets.scotland.load()
    X = data.exog
    y = data.endog
    data.exog = sm.add_constant(data.exog)
    gamma_model = sm.GLM(data.endog, data.exog, family=sm.families.Gamma())
    gamma_results = gamma_model.fit()

    regression_model = RegressionGLM(
        penalty=0.0,
        offset_mode='BASIC',
        family_name='gamma',
        binomial_link=None,
        gamma_link='inverse_power',
        gaussian_link=None,
        inverse_gaussian_link=None,
        poisson_link=None,
        negative_binomial_link=None,
        tweedie_link=None,
        alpha=1,
        power=1,
        var_power=1)

    regression_model.fit(X, y)

    assert regression_model.fitted_model.summary().as_csv() == gamma_results.summary().as_csv()

def test_regression_regularized():
    data = sm.datasets.scotland.load()
    X = data.exog
    y = data.endog
    penalty = 0.001
    data.exog = sm.add_constant(data.exog)
    gaussian_model = sm.GLM(data.endog, data.exog, family=sm.families.Gaussian())
    gaussian_results = gaussian_model.fit_regularized(alpha=penalty)

    regression_model = RegressionGLM(
        penalty=penalty,
        offset_mode='BASIC',
        family_name='gaussian',
        binomial_link=None,
        gamma_link=None,
        gaussian_link='identity',
        inverse_gaussian_link=None,
        poisson_link=None,
        negative_binomial_link=None,
        tweedie_link=None,
        alpha=1,
        power=1,
        var_power=1)

    regression_model.fit(X, y)

    for param1, param2 in zip(regression_model.fitted_model.params, gaussian_results.params):
        assert param1 == param2


def test_regression_offset():
    data = sm.datasets.scotland.load()
    X = data.exog
    y = data.endog
    offset = data.exog[:, 0]
    exog = data.exog[:, 1:]
    exog = sm.add_constant(exog)
    gaussian_model = sm.GLM(data.endog, exog, family=sm.families.Gaussian(), offset=offset)
    gaussian_results = gaussian_model.fit()

    regression_model = RegressionGLM(
        penalty=0.0,
        offset_mode='OFFSET',
        family_name='gaussian',
        binomial_link=None,
        gamma_link=None,
        gaussian_link='identity',
        inverse_gaussian_link=None,
        poisson_link=None,
        negative_binomial_link=None,
        tweedie_link=None,
        alpha=1,
        power=1,
        var_power=1,
        offset_column='COUTAX')

    regression_model.column_labels = data.exog_name

    regression_model.fit(X, y)

    assert regression_model.fitted_model.summary().as_csv() == gaussian_results.summary().as_csv()


def test_regression_exposure():
    data = sm.datasets.scotland.load()
    X = data.exog
    y = data.endog
    exposure = data.exog[:, 0]
    exog = data.exog[:, 1:]
    exog = sm.add_constant(exog)
    poisson_model = sm.GLM(data.endog, exog, family=sm.families.Poisson(sm.families.links.log()), exposure=exposure)
    poisson_results = poisson_model.fit()

    regression_model = RegressionGLM(
        penalty=0.0,
        offset_mode='EXPOSURE',
        family_name='poisson',
        binomial_link=None,
        gamma_link=None,
        gaussian_link=None,
        inverse_gaussian_link=None,
        poisson_link='log',
        negative_binomial_link=None,
        tweedie_link=None,
        alpha=1,
        power=1,
        var_power=1,
        exposure_column='COUTAX')

    regression_model.column_labels = data.exog_name

    regression_model.fit(X, y)

    assert regression_model.fitted_model.summary().as_csv() == poisson_results.summary().as_csv()

def test_regression_prediction():
    data = sm.datasets.scotland.load()
    X = data.exog
    y = data.endog
    exposure = data.exog[:, 0]
    exog = data.exog[:, 1:]
    exog = sm.add_constant(exog)
    poisson_model = sm.GLM(data.endog, exog, family=sm.families.Poisson(sm.families.links.log()), exposure=exposure)
    poisson_results = poisson_model.fit()

    regression_model = RegressionGLM(
        penalty=0.0,
        offset_mode='EXPOSURE',
        family_name='poisson',
        binomial_link=None,
        gamma_link=None,
        gaussian_link=None,
        inverse_gaussian_link=None,
        poisson_link='log',
        negative_binomial_link=None,
        tweedie_link=None,
        alpha=1,
        power=1,
        var_power=1,
        exposure_column='COUTAX')

    regression_model.column_labels = data.exog_name

    regression_model.fit(X, y)
    predictions = regression_model.predict(X)
    predictions_test = poisson_results.predict(exog, exposure=exposure)

    for pred1, pred2 in zip(predictions, predictions_test):
        assert pred1 == pred2