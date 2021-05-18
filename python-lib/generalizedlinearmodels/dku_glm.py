import statsmodels.api as sm
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
import pandas as pd


class BinaryClassificationGLM(BaseEstimator, ClassifierMixin):
    
    def __init__(self, link, family, alpha, power, var_power):

        self.link = link
        self.family = family
        self.alpha = alpha
        self.power = power
        self.var_power = var_power
        self.fit_intercept=True
        self.intercept_scaling = 1
        self.fitted_model = None
        self.coef_= None
        self.intercept_ = None
        self.classes_ = None

        
    def get_link(self):
        """ 
        gets the statsmodel link function based on the
        user defined link on the model training screen   
        """ 
        links_dict = {
            'cloglog': sm.families.links.cloglog(),
            'log': sm.families.links.log(),
            'logit': sm.families.links.logit(),
            'negative_binomial': sm.families.links.NegativeBinomial(self.alpha),
            'power': sm.families.links.Power(self.power),
            'cauchy': sm.families.links.cauchy(),
            'identity': sm.families.links.identity(),
            'inverse_power': sm.families.links.inverse_power(),
            'inverse_squared': sm.families.links.inverse_squared()
        }
        
        return links_dict[self.link]
        
    def get_family(self, link):
        """ 
        takes in user defined family variable 
        and statsmodel link function
        returns the family 
        """       
        if self.family == 'binomial':
            return sm.families.Binomial(link=link)
        
        elif self.family == "gamma":
            return sm.families.Gamma(link=link)
        
        elif self.family == "gaussian":
            return sm.families.Gaussian(link=link)
        
        elif self.family == "inverse_gaussian": 
            return sm.families.InverseGaussian(link=link) 
        
        elif self.family == "negative_binomial": 
            return sm.families.NegativeBinomial(link=link, alpha=self.alpha)
        
        elif self.family == "poisson":
            return sm.families.Poisson(link=link) 
        
        elif self.family == "tweedie":
            return sm.families.Tweedie(link=link, var_power=self.var_power)
        else:
            exit()
    
    def fit(self, X, y):
        """ 
        takes in training data and fits a model
        """     
    
        self.classes_ = list(set(y))
         
        X = sm.add_constant(X)
        
        #  returns statsmodel link and distribution functions based on user input
        link = self.get_link()
        family = self.get_family(link)

        #  fits and stores statsmodel glm
        model = sm.GLM(y, X, family=family)
        self.fitted_model = model.fit()
        
        #  adds attributes for explainability
        self.coef_ = np.array(self.fitted_model.params[1:]).reshape(1, -1)     #removes first value which is the intercept 
        self.intercept_ = np.array(self.fitted_model.params[0]).reshape(-1)

    
    def predict(self, X):
        """ 
        Returns the binary target
        """

        X = sm.add_constant(X, has_constant='add')
        
        # makes predictions and converts to DSS accepted format      
        y_pred = np.array(self.fitted_model.predict(X))
        y_pred_final = y_pred.reshape((len(y_pred), -1))
        
        return y_pred_final>0.5
           

    def predict_proba(self, X):
        """
        Return the prediction proba
        """
        #  adds a constant 
        X = sm.add_constant(X, has_constant='add')
        
        # makes predictions and converts to DSS accepted format 
        y_pred = np.array(self.fitted_model.predict(X))
        y_pred_final = y_pred.reshape((len(y_pred), -1))
        
        # returns p, 1-p prediction probabilities
        return np.append(1-y_pred_final, y_pred_final, axis=1)
    
    
    
    
    
class RegressionGLM(BaseEstimator, ClassifierMixin):
    
    def __init__(self, link, family, alpha, power, var_power):

        self.link = link
        self.family = family
        self.alpha = alpha
        self.power = power
        self.var_power = var_power
        self.fit_intercept=True
        self.intercept_scaling = 1
        self.fitted_model = None
        self.coef_= None
        self.intercept_ = None
        self.classes_ = None

        
    def get_link(self):
        """ 
        gets the statsmodel link function based on the
        user defined link on the model training screen   
        """ 
        links_dict = {
            'cloglog': sm.families.links.cloglog(),
            'log': sm.families.links.log(),
            'logit': sm.families.links.logit(),
            'negative_binomial': sm.families.links.NegativeBinomial(self.alpha),
            'power': sm.families.links.Power(self.power),
            'cauchy': sm.families.links.cauchy(),
            'identity': sm.families.links.identity(),
            'inverse_power': sm.families.links.inverse_power(),
            'inverse_squared': sm.families.links.inverse_squared()
        }
        
        return links_dict[self.link]
        
    def get_family(self, link):
        """ 
        takes in user defined family variable 
        and statsmodel link function
        returns the family 
        """       
        if self.family == 'binomial':
            return sm.families.Binomial(link=link)
        
        elif self.family == "gamma":
            return sm.families.Gamma(link=link)
        
        elif self.family == "gaussian":
            return sm.families.Gaussian(link=link)
        
        elif self.family == "inverse_gaussian": 
            return sm.families.InverseGaussian(link=link) 
        
        elif self.family == "negative_binomial": 
            return sm.families.NegativeBinomial(link=link, alpha=self.alpha)
        
        elif self.family == "poisson":
            return sm.families.Poisson(link=link)
        
        elif self.family == "tweedie":
            return sm.families.Tweedie(link=link, var_power=self.var_power)
        else:
            exit()
            
    
    def fit(self, X, y):
        """ 
        takes in training data and fits a model
        """     
    
        self.classes_ = list(set(y))
         
        X = sm.add_constant(X)
        
        #  returns statsmodel link and distribution functions based on user input
        link = self.get_link()
        family = self.get_family(link)

        #  fits and stores statsmodel glm
        model = sm.GLM(y, X, family=family)
        self.fitted_model = model.fit()
        
        #  adds attributes for explainability
        # intercept cant be multidimensional np array like in classification
        # as scoring_base.py func compute_lm_significant hstack method will fail 
        self.coef_ = np.array(self.fitted_model.params[1:])   #removes first value which is the intercept 
        self.intercept_ = float(self.fitted_model.params[0])

    
    def predict(self, X):
        """ 
        Returns the target as 1D array
        """

        X = sm.add_constant(X, has_constant='add')
        
        # makes predictions and converts to DSS accepted format      
        y_pred = np.array(self.fitted_model.predict(X))

        return y_pred
           

    
    