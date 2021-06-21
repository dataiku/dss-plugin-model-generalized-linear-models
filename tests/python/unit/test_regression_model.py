from python-lib.generalized_linear_models.dku_glm import RegressionGLM
import statsmodel.api as sm
import unittest
from testing_utils import testing_dict

def test_link_function():
    case = unittest.TestCase()
    expected = [
        sm.families.links.log(),
        sm.families.links.identity(),
        sm.families.links.inverse_power(),
        sm.families.links.inverse_squared(),
        sm.families.links.log(),
        sm.families.links.cloglog(),
        sm.families.links.Power(1),
    ]

    actual = []
    for test in testing_dict:
        regression_model = RegressionGLM(
            family=test['family'],
            binomial_link=test['binomial_link'],
            gamma_link=test['gamma_link'],
            gaussian_link=['gaussian_link'],
            inverse_gaussian_link=['inverse_gaussian_link'],
            poisson_link=['poisson_link'],
            negative_binomial_link=['negative_binomial_link'],
            tweedie_link=['tweedie_link'],
            alpha=1,
            power=1,
            var_power=1
        )
        regression_model.set_link_str()
        actual.append(regression_model.get_link())

    case.assertItemsEqual(actual, expected)

