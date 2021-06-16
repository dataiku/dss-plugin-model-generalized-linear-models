# This file is the actual code for the custom Python algorithm dev-glm_glm
from dataiku.doctor.plugins.custom_prediction_algorithm import BaseCustomPredictionAlgorithm
from generalized_linear_models.dku_glm import RegressionGLM

class CustomPredictionAlgorithm(BaseCustomPredictionAlgorithm):    
    
    def __init__(self, prediction_type=None, params=None):   
        
        self.params = params
        self.clf = RegressionGLM(
            link=params.get("link"),
            family=params.get("family"),
            alpha=params.get("alpha"),
            power=params.get("power"),
            var_power=params.get("var_power")
        )
        super(CustomPredictionAlgorithm, self).__init__(prediction_type, self.params)
                                     
    def get_clf(self):

        return self.clf