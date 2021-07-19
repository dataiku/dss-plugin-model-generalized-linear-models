import sys
sys.path.append("..")
print('\n'.join(sys.path))
from generalized_linear_models.dku_glm import BinaryClassificationGLM
import statsmodels.api as sm
import unittest
from testing_utils import testing_dict_binary
import numpy as np
import pandas as pd
from sklearn import datasets

def test_link_function():
    case = unittest.TestCase()
    expected = [
        type(sm.families.Binomial()),
        type(sm.families.links.log())
    ]

    actual = []

    breast_cancer = datasets.load_breast_cancer()
    X, y = breast_cancer.data, breast_cancer.target

    for test in testing_dict_binary:
        test_params = testing_dict_binary[test]
        binary_model = BinaryClassificationGLM(
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
            var_power=1
        )
        binary_model.fit_model(X, y)
        actual.append(type(binary_model.family))
        actual.append(type(binary_model.family.link))

    case.assertListEqual(actual, expected)

