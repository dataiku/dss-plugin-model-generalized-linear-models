import sys
sys.path.append("..")
print('\n'.join(sys.path))
from generalized_linear_models.dku_glm import BinaryClassificationGLM
import statsmodels.api as sm
import unittest
