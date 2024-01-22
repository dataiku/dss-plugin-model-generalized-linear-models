import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
import statsmodels
import logging

class RelativityCalculator:
    """
    A class to calculate relativities for model variables based on their coefficients.

    Attributes:
        coefficients (list): The list of model coefficients.
        variable_names (list): The list of variable names corresponding to the coefficients.
        base_values (list): The list of base values for each variable.
        link_function (function): The link function to apply to coefficients.
    """

    def __init__(self, coefficients, base_values, link_function):
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
        logging.info(f"the link function is {self.link_function}")

    def get_link_function_operation(self, link_function):
        """
        Maps string-based link functions to their corresponding mathematical operations.
        """
        if link_function == 'log':
            return lambda x: np.exp(x)
        elif link_function == 'identity':
            return lambda x: x
        elif link_function == 'logit':
            return lambda x: np.exp(x) / (1 + np.exp(x))
        # Add other string-based link functions here
        else:
            raise NotImplementedError("String-based link function not supported: " + link_function)

    def calculate_relativities(self):
        """
        Calculates and returns relativities for each model variable.
        """
        baseline = np.dot(self.coefficients, self.base_values)

        if isinstance(self.link_function, str):
            # If the link function is a string, use the mapped operation
            link_function_operation = self.get_link_function_operation(self.link_function)
            relativities = link_function_operation(self.coefficients) / link_function_operation(baseline)
        elif hasattr(self.link_function, '__call__'):
            # If the link function is a callable (glum method), use it directly
            baseline_transformed = self.link_function(baseline)
            relativities = self.link_function(self.coefficients) / baseline_transformed
        else:
            raise NotImplementedError("Link function type not supported")

        return dict(zip(self.variable_names, relativities))