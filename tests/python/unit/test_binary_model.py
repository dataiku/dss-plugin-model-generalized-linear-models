from generalized_linear_models.dku_glm import BinaryClassificationGLM
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
        binary_model = BinaryClassificationGLM(
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
        binary_model.assign_family()
        actual.append(binary_model.get_link_function())

    for act, exp in zip(actual, expected):
        assert type(act) == type(exp)

def test_classification():
    data = sm.datasets.ccard.load()
    X = data.exog[:, :3]
    y = data.exog[:, 3]
    endog = data.exog[:, 3]
    exog = sm.add_constant(data.exog[:, :3])
    logistic_model = sm.GLM(endog, exog, family=sm.families.Binomial(sm.families.links.logit()))
    logistic_results = logistic_model.fit()

    binary_model = BinaryClassificationGLM(
        penalty=0.0,
        offset_mode='BASIC',
        family_name='binomial',
        binomial_link='logit',
        gamma_link=None,
        gaussian_link=None,
        inverse_gaussian_link=None,
        poisson_link=None,
        negative_binomial_link=None,
        tweedie_link=None,
        alpha=1,
        power=1,
        var_power=1)

    binary_model.fit(X, y)

    assert binary_model.fitted_model.summary().as_csv() == logistic_results.summary().as_csv()


def test_classification_prediction():
    data = sm.datasets.ccard.load()
    X = data.exog[:, :3]
    y = data.exog[:, 3]
    endog = data.exog[:, 3]
    exog = sm.add_constant(data.exog[:, :3])
    logistic_model = sm.GLM(endog, exog, family=sm.families.Binomial(sm.families.links.logit()))
    logistic_results = logistic_model.fit()

    binary_model = BinaryClassificationGLM(
        penalty=0.0,
        offset_mode='BASIC',
        family_name='binomial',
        binomial_link='logit',
        gamma_link=None,
        gaussian_link=None,
        inverse_gaussian_link=None,
        poisson_link=None,
        negative_binomial_link=None,
        tweedie_link=None,
        alpha=1,
        power=1,
        var_power=1)

    binary_model.fit(X, y)
    predictions = binary_model.predict(X)
    predictions_test = [x>0.5 for x in logistic_results.predict(exog)]

    for pred1, pred2 in zip(predictions, predictions_test):
        assert pred1 == pred2
