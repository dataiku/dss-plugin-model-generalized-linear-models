import sys
sys.path.append("..")
print('\n'.join(sys.path))
from generalized_linear_models.dku_glm import RegressionGLM
import statsmodels.api as sm
import unittest
from testing_utils import testing_dict_regression
