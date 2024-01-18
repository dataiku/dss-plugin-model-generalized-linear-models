import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu

class RelativityCalculator:
    """
    A class to calculate relativities for model variables based on their coefficients.

    Attributes:
        coefficients (list): The list of model coefficients.
        variable_names (list): The list of variable names corresponding to the coefficients.
        base_values (list): The list of base values for each variable.
        link_function (function): The link function to apply to coefficients.
    """

    def __init__(self, coefficients, base_values, link_function=np.exp):
        """
        Initializes the RelativityCalculator with model coefficients and base values.

        Args:
            coefficients (dict): A dictionary of model coefficients.
            base_values (dict): A dictionary of base values for model variables.
            link_function (function, optional): The link function to use. Defaults to np.exp.
        """
        self.coefficients = list(coefficients.values())
        self.variable_names = list(coefficients.keys())
        self.base_values = list(base_values.values())
        self.link_function = link_function

    def calculate_relativities(self):
        """
        Calculates and returns relativities for each model variable.

        Returns:
            dict: A dictionary mapping variable names to their relativities.
        """
        baseline = self.link_function(np.dot(self.coefficients, self.base_values))
        relativities = np.exp(self.coefficients) / baseline
        return dict(zip(self.variable_names, relativities))