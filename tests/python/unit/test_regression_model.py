from python-prediction-algo.glm-regression import CustomPredictionAlgorithm
import statsmodel.api as sm
import unittest

def test_link_function():
    case = unittest.TestCase()
    expected = [
        sm.families.links.cloglog(),
        sm.families.links.log(),
        sm.families.links.logit(),
        sm.families.links.NegativeBinomial(1),
        sm.families.links.Power(1),
        sm.families.links.cauchy(),
        sm.families.links.identity(),
        sm.families.links.inverse_power(),
        sm.families.links.inverse_squared()
    ]

    link_strings =[
        'cloglog',
        'log',
        'logit',
        'negative_binomial',
        'power',
        'cauchy',
        'identity',
        'inverse_power',
        'inverse_squared'
    ]

    actual = []
    for link in link_strings:
        binary_model = CustomPredictionAlgorithm(
            link=link,
            family='binomial',
            alpha=1,
            power=1,
            var_power=1
        )
        actual.append(binary_model.get_link())

    case.assertItemsEqual(actual, expected)