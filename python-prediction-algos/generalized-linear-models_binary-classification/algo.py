from dataiku.doctor.plugins.custom_prediction_algorithm import BaseCustomPredictionAlgorithm
from generalized_linear_models.dku_glm import BinaryClassificationGLM


class CustomPredictionAlgorithm(BaseCustomPredictionAlgorithm):

    def __init__(self, prediction_type=None, params=None):
        self.params = params
        for penalty_value in self.params['penalty']:
            if penalty_value < 0:
                raise ValueError("Negative values for the regularization penalty are not supported")
        self.clf = BinaryClassificationGLM(**params)
        super(CustomPredictionAlgorithm, self).__init__(prediction_type, self.params)

    def get_clf(self):
        return self.clf