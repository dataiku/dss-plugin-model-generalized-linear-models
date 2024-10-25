import numpy as np

class ModelMetricsCalculator:
    def __init__(self, model_retriever):
        self.model_info_handler = model_retriever.model_info_handler
        self.predictor = model_retriever.model_info_handler.get_predictor()
        self.df = self.model_info_handler.get_train_df()[0]
        self.transformed_X, _, _, self.valid_y = self.predictor.preprocessing.preprocess(self.df, with_target=True)
        self.transformed_X = self.predictor._clf.process_fixed_columns(self.transformed_X)
        self.predictions = self.predictor._clf.fitted_model.predict(self.transformed_X)
        
    def calculate_aic(self):
        aic_value = np.round(self.predictor._clf.fitted_model.aic(self.transformed_X, self.valid_y), 2)
        return aic_value
    
    def calculate_bic(self):
        bic_value = np.round(self.predictor._clf.fitted_model.bic(self.transformed_X, self.valid_y), 2)
        return bic_value
    
    def calculate_deviance(self):
        deviance_value = np.round(self.predictor._clf.family_glum_class.deviance(self.valid_y, self.predictions), 2)
        return deviance_value
    
    def calculate_metrics(self):
        deviance_value = self.calculate_deviance()
        aic_value = self.calculate_aic()
        bic_value = self.calculate_bic()
        

        
        return aic_value, bic_value, deviance_value