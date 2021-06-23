from dataiku.doctor.plugins.custom_prediction_algorithm import BaseCustomPredictionAlgorithm
from generalized_linear_models.dku_glm import RegressionGLM


class CustomPredictionAlgorithm(BaseCustomPredictionAlgorithm):

    def __init__(self, prediction_type=None, params=None):
        self.params = params
        self.clf = RegressionGLM(
            family_name=params.get("family"),
            binomial_link=params.get("binomial_link"),
            gamma_link=params.get("gamma_link"),
            gaussian_link=params.get("gaussian_link"),
            inverse_gaussian_link=params.get("inverse_gaussian_link"),
            poisson_link=params.get("poisson_link"),
            negative_binomial_link=params.get("negative_binomial_link"),
            tweedie_link=params.get("tweedie_link"),
            alpha=params.get("alpha"),
            power=params.get("power"),
            var_power=params.get("var_power")
        )
        super(CustomPredictionAlgorithm, self).__init__(prediction_type, self.params)

    def get_clf(self):
        return self.clf