import statsmodels.api as sm
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
import pandas as pd


class BaseGLM(BaseEstimator, ClassifierMixin):
    """
    Base class for GLM
    Binary and Regression GLM inherit from here
    """

    def __init__(self, family_name, binomial_link, gamma_link, gaussian_link, inverse_gaussian_link,
                 poisson_link,negative_binomial_link, tweedie_link, alpha, power, penalty,
                 var_power, training_dataset, offset_column=None, exposure_column=None,
                 important_column=None, column_labels=None):
        self.family_name = family_name
        self.binomial_link = binomial_link
        self.gamma_link = gamma_link
        self.gaussian_link = gaussian_link
        self.inverse_gaussian_link = inverse_gaussian_link
        self.poisson_link = poisson_link
        self.negative_binomial_link = negative_binomial_link
        self.tweedie_link = tweedie_link
        self.family = None
        self.alpha = alpha
        self.power = power
        self.penalty = penalty
        self.var_power = var_power
        self.fit_intercept = True
        self.intercept_scaling = 1
        self.fitted_model = None
        self.coef_ = None
        self.intercept_ = None
        self.classes_ = None
        self.offset_column = offset_column
        self.offset_index = None
        self.exposure_column = exposure_column
        self.exposure_index = None
        self.column_labels = column_labels
        self.training_dataset = training_dataset
        self.removed_indices = None

    def get_link_function(self):
        """
        gets the statsmodel link function based on the
        user defined link on the model training screen
        """
        family_2_link_dict = {
            'binomial': self.binomial_link,
            'gamma': self.gamma_link,
            'gaussian': self.gaussian_link,
            'inverse_gaussian': self.inverse_gaussian_link,
            'poisson': self.poisson_link,
            'negative_binomial': self.negative_binomial_link,
            'tweedie': self.tweedie_link
        }

        user_link = family_2_link_dict[self.family_name]

        if user_link == 'cloglog':
            return sm.families.links.cloglog()
        elif user_link == 'log':
            return sm.families.links.log()
        elif user_link == 'logit':
            return sm.families.links.logit()
        elif user_link == 'negative_binomial':
            return sm.families.links.NegativeBinomial(self.alpha)
        elif user_link == 'power':
            return sm.families.links.Power(self.power)
        elif user_link == 'cauchy':
            return sm.families.links.cauchy()
        elif user_link == 'identity':
            return sm.families.links.identity()
        elif user_link == 'inverse_power':
            return sm.families.links.inverse_power()
        elif user_link == 'inverse_squared':
            return sm.families.links.inverse_squared()


    def get_family(self, link):
        """
        takes in user defined family variable
        and statsmodel link function
        returns the family
        """
        if self.family_name == 'binomial':
            return sm.families.Binomial(link=link)

        elif self.family_name == "gamma":
            return sm.families.Gamma(link=link)

        elif self.family_name == "gaussian":
            return sm.families.Gaussian(link=link)

        elif self.family_name == "inverse_gaussian":
            return sm.families.InverseGaussian(link=link)

        elif self.family_name == "negative_binomial":
            return sm.families.NegativeBinomial(link=link, alpha=self.alpha)

        elif self.family_name == "poisson":
            return sm.families.Poisson(link=link)

        elif self.family_name == "tweedie":
            return sm.families.Tweedie(link=link, var_power=self.var_power)
        else:
            raise ValueError("Unsupported family")

    def assign_family(self):
        """
        converts string inputs of family & link
        in to statsmodel family and makes it an attribute
        """
        link = self.get_link_function()
        self.family = self.get_family(link)

    def get_x_column(self, X, important_column):
        """
        returns an array of values specified by column name provided
        by the user
        """
        if important_column == None:
            column_values = None
            column_index = None

        elif important_column not in self.column_labels:
            raise ValueError(f'The column name provided: [{important_column}], is not present in the list of columns from the dataset. Please chose one of:{self.column_labels}')
        else:
            column_index = self.column_labels.index(important_column)
            column_values = X[:, column_index]

        return column_values, column_index

        return column_values

    def fit_model(self, X, y, sample_weight=None):
        """
        fits a GLM model
        """
        self.classes_ = list(set(y))

        self.assign_family()
        
        offset, self.offset_index = self.get_x_column(X, self.offset_column)
        exposure, self.exposure_index = self.get_x_column(X, self.exposure_column)
        self.removed_indices = []
        if self.offset_index is not None:
            self.removed_indices.append(self.offset_index)
        if self.exposure_index is not None:
            if self.exposure_index != self.offset_index:
                self.removed_indices.append(self.exposure_index)
        
        if len(self.removed_indices)>0:
            X = np.delete(X, self.removed_indices, axis=1)
            #for index in sorted(self.removed_indices, reverse=True):
            #    del self.column_labels[index]
        
        X = sm.add_constant(X)
        
        #  fits and stores statsmodel glm
        model = sm.GLM(y, X, family=self.family, offset=offset, exposure=exposure, var_weights=sample_weight)
        
        self.fitted_model = model.fit_regularized(method='elastic_net', alpha=self.penalty)
        
    def set_column_labels(self, column_labels):
        # in order to preserve the attribute `column_labels` when cloning
        # the estimator, we have declared it as a keyword argument in the
        # `__init__` and set it there
        self.column_labels = column_labels
    
    def process_fixed_columns(self, X):
        removed_indices = []
        if self.offset_index is not None:
            removed_indices.append(self.offset_index)
        if self.exposure_index is not None:
            if self.exposure_index != self.offset_index:
                removed_indices.append(self.exposure_index)
        if len(removed_indices)>0:
            X = np.delete(X, removed_indices, axis=1)
        return X

class BinaryClassificationGLM(BaseGLM):

    def fit(self, X, y, sample_weight=None):
        """
        takes in training data and fits a model
        """
        self.fit_model(X, y, sample_weight)
        
        #  adds attributes for explainability
        self.coef_ = np.array(self.fitted_model.params[1:]).reshape(1,
                                                                    -1)  # removes first value which is the intercept
        self.intercept_ = np.array(self.fitted_model.params[0]).reshape(-1)

    def predict(self, X):
        """
        Returns the binary target
        """
        X = self.process_fixed_columns(X)
        
        X = sm.add_constant(X, has_constant='add')

        # makes predictions and converts to DSS accepted format
        y_pred = np.array(self.fitted_model.predict(X))
        y_pred_final = y_pred.reshape((len(y_pred), -1))

        return y_pred_final > 0.5

    def predict_proba(self, X):
        """
        Return the prediction proba
        """
        X = self.process_fixed_columns(X)
        #  adds a constant
        X = sm.add_constant(X, has_constant='add')

        # makes predictions and converts to DSS accepted format
        y_pred = np.array(self.fitted_model.predict(X))
        y_pred_final = y_pred.reshape((len(y_pred), -1))

        # returns p, 1-p prediction probabilities
        return np.append(1 - y_pred_final, y_pred_final, axis=1)


class RegressionGLM(BaseGLM):

    def fit(self, X, y, sample_weight=None):
        """
        takes in training data and fits a model
        """
        self.fit_model(X, y, sample_weight)
        X = self.process_fixed_columns(X)
        
        self.coef_ = np.array(self.fitted_model.params[1:])  # removes first value which is the intercept
        # insert 0 coefs for exposure and offset
        if len(self.removed_indices) > 0:
            self.coef_ = np.insert(self.coef_, self.removed_indices, 0)

        self.intercept_ = float(self.fitted_model.params[0])

    def predict(self, X):
        """
        Returns the target as 1D array
        """
        
        offset, self.offset_index = self.get_x_column(X, self.offset_column)
        exposure, self.exposure_index = self.get_x_column(X, self.exposure_column)
        X = self.process_fixed_columns(X)
        X = sm.add_constant(X, has_constant='add')
        
        # makes predictions and converts to DSS accepted format
        y_pred = np.array(self.fitted_model.predict(X, offset=offset, exposure=exposure))

        return y_pred





