import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from glm_handler.dku_utils import extract_active_fullModelId
from logging_assist.logging import logger
from time import time

class RelativitiesCalculator:
    """
    A class to handle interactions with a Dataiku model.

    Attributes:
        model_id (str): The ID of the model.
        model (dataiku.Model): The Dataiku model object.
        full_model_id (str): The full model ID of the active model version.
        model_info_handler (PredictionModelInformationHandler): Handler for model information.
    """

    def __init__(self,data_handler, model_retriever):
        """
        Initializes the ModelHandler with a specific model ID.

        Args:
            model_id (str): The ID of the model to handle.
        """
        self.data_handler = data_handler
        self.base_values = {}
        self.modalities = {}
        self.model_retriever = model_retriever
        self.train_set = self.prepare_train_set()
        self.test_set = self.prepare_test_set()
        self.compute_base_values()
        logger.info("ModelHandler initialized.")
    

    def compute_base_values(self):
        """
        Main method to initialize and compute base values.
        """
        logger.info("Computing base values.")
        self.handle_preprocessing()
        self.compute_numerical_features()
        logger.info(f"Base values computed: {self.base_values}")


    def handle_preprocessing(self):
        """
        Processes each step in the preprocessing pipeline.
        """
        logger.info("Handling preprocessing steps.")
        preprocessing = self.model_retriever.predictor.get_preprocessing()
        for step in preprocessing.pipeline.steps:
            self.process_preprocessing_step(step)
        logger.info("Preprocessing handled.")

    def process_preprocessing_step(self, step):
        """
        Processes a single preprocessing step to extract base values and modalities.

        Args:
            step: A preprocessing step in the pipeline.
        """
        try:
            logger.info(f"Processing preprocessing step: {step}")
            self.base_values[step.input_col] = step.processor.mode_column
            self.modalities[step.input_col] = step.processor.modalities
            logger.info(f"Step processed: {step}")
        except AttributeError:
            logger.info(f"Step processing failed (AttributeError): {step}")

    def compute_numerical_features(self):
        """
        Computes base values for numerical features not handled in preprocessing.
        """
        logger.info("Computing numerical features.")
#         used_features = self.model_retriever.get
        for feature in self.model_retriever.used_features:
            if feature not in self.base_values:
                self.compute_base_for_feature(feature, self.train_set)
        logger.info(f"Numerical features computed: {self.base_values}")
        
        
    def compute_base_for_feature(self, feature, train_set):
        """
        Computes base value for a single feature based on its type and rescaling.

        Args:
            feature (str): The feature to compute the base value for.
            train_set (pd.DataFrame): The training dataset.
        """
        if self.model_retriever.features[feature]['type'] == 'NUMERIC' and self.model_retriever.features[feature]['rescaling'] == 'NONE':
            self.compute_base_for_numeric_feature(feature, train_set)
        else:
            error_msg = f"feature should be handled numerically without rescaling or categorically with the custom preprocessor for model {self.model_retriever.full_model_id}"
            logger.error(error_msg)
            raise Exception(error_msg)


 
    def compute_base_for_numeric_feature(self, feature, train_set):
        """
        Computes base values for numeric features without rescaling.

        Args:
            feature (str): The numeric feature to compute the base value for.
            train_set (pd.DataFrame): The training dataset.
        """
        logger.info(f"Computing base value for numeric feature: {feature}")
        if self.model.retriever.exposure_columns is not None:
            feature_exposure = train_set.groupby(feature)[self.model_retriever.exposure_columns].sum().reset_index()
            base_value = feature_exposure[feature].iloc[feature_exposure[self.model_retriever.exposure_columns].idxmax()]
        else:
            feature_exposure = train_set[feature].value_counts().reset_index()
            base_value = feature_exposure['index'].iloc[feature_exposure[feature].idxmax()]

        self.base_values[feature] = base_value
        self.modalities[feature] = {'min': train_set[feature].min(), 'max': train_set[feature].max()}
        logger.info(f"Base value computed for numeric feature: {feature}, base_value: {base_value}")

    def get_relativities_df(self):
        """
        Computes and returns the relativities DataFrame for the model.

        Returns:
            pd.DataFrame: The relativities DataFrame.
        """
        logger.info("Computing relativities DataFrame.")
        sample_train_row = self.initialize_baseline()
        baseline_prediction = self.calculate_baseline_prediction(sample_train_row)
        self.calculate_relative_predictions(sample_train_row, baseline_prediction)
        relativities_df = self.construct_relativities_df()

        logger.info(f"Relativities DataFrame computed: {relativities_df}")
        return relativities_df

    def initialize_baseline(self):
        logger.info("initialize_baseline")
        train_row = self.train_set.head(1).copy()
        for feature in self.base_values.keys():
            train_row[feature] = self.base_values[feature]
        if self.model_retriever.exposure_columns is not None:
            train_row[self.model_retriever.exposure_columns] = 1
        logger.info("Successfully initialize_baseline")
        return train_row

    def calculate_baseline_prediction(self, sample_train_row):
        logger.info("Calculating baseline prediction")
        return self.model_retriever.predictor.predict(sample_train_row).iloc[0][0]

    def calculate_relative_predictions(self, sample_train_row, baseline_prediction):
        logger.info("Calculating relativity prediction")
        self.relativities = {'base': {'base': baseline_prediction}}
        for feature in self.base_values.keys():
            self.relativities[feature] = {self.base_values[feature]: 1.0}
            if self.model_retriever.features[feature]['type'] == 'CATEGORY':    
                for modality in self.modalities[feature]:
                    train_row_copy = sample_train_row.copy()
                    train_row_copy[feature] = modality
                    prediction = self.model_retriever.predictor.predict(train_row_copy).iloc[0][0]
                    self.relativities[feature][modality] = prediction / baseline_prediction
            else:
                train_row_copy = sample_train_row.copy()
                unique_values = sorted(list(set(self.train_set[feature])))
                for value in unique_values:
                    train_row_copy[feature] = value
                    prediction = self.model_retriever.predictor.predict(train_row_copy).iloc[0][0]
                    self.relativities[feature][value] = prediction / baseline_prediction

    def construct_relativities_df(self):
        logger.info("constructing relativites DF")
        rel_df = pd.DataFrame(columns=['feature', 'value', 'relativity'])
        for feature, values in self.relativities.items():
            for value, relativity in values.items():
                rel_df = rel_df.append({'feature': feature, 'value': value, 'relativity': relativity}, ignore_index=True)
        rel_df.coluns = ['variable', 'category', 'relativity']
        return rel_df

    def apply_weights_to_data(self, test_set):
        used_features = list(self.base_values.keys())
        if self.model_retriever.exposure_columns is None:
            test_set['weight'] = 1
        else:
            test_set['weight'] = test_set[self.model_retriever.exposure]
        test_set['weighted_target'] = test_set[self.model_retriever.target_columns] * test_set['weight']
        test_set['weighted_predicted'] = test_set['predicted'] * test_set['weight']

    def prepare_final_data(self, test_set, feature, nb_bins_numerical, base_predictions):
        test_set = pd.concat([test_set, base_predictions], axis=1)
        test_set['base_' + feature] *= test_set['weight']
        test_set[feature] = pd.cut(test_set[feature], bins=nb_bins_numerical).apply(lambda x: (x.left + x.right) / 2 if isinstance(x, pd.Interval) else x)
        predicted_base = self.aggregate_data(test_set, feature)
        return self.update_feature_dataset(predicted_base, feature)

    def aggregate_data(self, test_set, feature):
        group_data = test_set.groupby(feature).agg({
            'weighted_target': 'sum',
            'weighted_predicted': 'sum',
            'weight': 'sum',
            'base_' + feature: 'sum'
        }).reset_index()
        group_data['weighted_target'] /= group_data['weight']
        group_data['weighted_predicted'] /= group_data['weight']
        group_data['base_' + feature] /= group_data['weight']
        return group_data.rename(columns={'base_' + feature: 'weighted_base'})

    def update_feature_dataset(self, group_data, feature):
        predicted_base_df = pd.DataFrame(columns=['feature', 'category', 'target', 'predicted', 'exposure', 'base'])
        group_data.columns = ['category', 'target', 'predicted', 'exposure', 'base']
        group_data['feature'] = feature
        self.predicted_base_df = self.predicted_base_df[self.predicted_base_df['feature'] != feature]
        self.predicted_base_df = self.predicted_base_df.append(group_data)
        return self.predicted_base_df


    def prepare_train_set(self):
        """
        Prepares and returns the training dataset.

        Returns:
            pd.DataFrame: The training dataset.
        """
        logger.info("Preparing training dataset.")
        train_set = self.model_retriever.model_info_handler.get_train_df()[0].copy()
        predicted = self.model_retriever.predictor.predict(train_set)
        train_set['predicted'] = predicted
        train_set['weight'] = 1 if self.model_retriever.exposure_columns is None else train_set[self.model_retriever.exposure_columns]
        train_set['weighted_target'] = train_set[self.model_retriever.target_column] * train_set['weight']
        train_set['weighted_predicted'] = train_set['predicted'] * train_set['weight']
        logger.info(f"Training dataset prepared: {train_set.shape}")
        return train_set

    def prepare_test_set(self):
        """
        Prepares and returns the test dataset.

        Returns:
            pd.DataFrame: The test dataset.
        """
        logger.info("Preparing test dataset.")
        test_set = self.model_retriever.model_info_handler.get_test_df()[0].copy()
        predicted = self.model_retriever.predictor.predict(test_set)
        test_set['predicted'] = predicted
        test_set['weight'] = 1 if self.model_retriever.exposure_columns is None else test_set[self.model_retriever.exposure_columns]
        test_set['weighted_target'] = test_set[self.model_retriever.target_column] * test_set['weight']
        test_set['weighted_predicted'] = test_set['predicted'] * test_set['weight']
        logger.info(f"Test dataset prepared: {test_set.shape}")
        return test_set
    
    def compute_base_predictions_new(self, test_set, used_features):
        logger.info("Computing base Predictions")
        base_data = dict()
        for feature in used_features:
            copy_test_df = test_set.copy()
            copy_test_df = copy_test_df.groupby(feature, as_index=False).first()
            copy_test_df[self.model_retriever.exposure_columns] = 1
            for other_feature in [col for col in used_features if col != feature]:
                copy_test_df[other_feature] = self.base_values[other_feature]
            predictions = self.model_retriever.predictor.predict(copy_test_df)
            base_data[feature] = pd.DataFrame(data={('base_' + feature): predictions['prediction'], feature: copy_test_df[feature]})
        logger.info("successfully computed base Predictions")
        return base_data

    def merge_predictions(self, test_set, base_data):
        logger.info("Merging Base predictions")
        for feature in base_data.keys():
            test_set = pd.merge(test_set, base_data[feature], how='left', on=feature)
        logger.info("Successfully Merged Base predictions")
        return test_set


    def get_predicted_and_base(self, nb_bins_numerical=100000):
        logger.info("Getting Predicted and base")
        
        step_time = time()
        self.compute_base_values()
        step_elapsed = time() - step_time
        logger.info(f"Step - Compute base values: {step_elapsed:.2f} seconds")
        
        step_time = time()
        test_set = self.test_set
        train_set = self.train_set
        used_features = list(self.base_values.keys())
        logger.info(f"Used features in predicted_vase are {used_features}")
        step_elapsed = time() - step_time
        logger.info(f"Step - Get datasets: {step_elapsed:.2f} seconds")
        
        step_time = time()
        base_data = self.compute_base_predictions_new(test_set, used_features)
        step_elapsed = time() - step_time
        logger.info(f"Step - compute base predictions: {step_elapsed:.2f} seconds")
        
        step_time = time()
        test_set = self.merge_predictions(test_set, base_data)
        logger.info(f"merged predictions")
        predicted_base = self.data_handler.calculate_weighted_aggregations(test_set, self.model_retriever.non_excluded_features, used_features)
        logger.info(f"calculate weighted aggregations")
        predicted_base_df = self.data_handler.construct_final_dataframe(predicted_base)
        logger.info(f"construct final dataframe")
        predicted_base_df['dataset'] = 'test'
        step_elapsed = time() - step_time
        logger.info(f"Step - finalize test predicted base: {step_elapsed:.2f} seconds")
        
        step_time = time()
        base_data_train = self.compute_base_predictions_new(train_set, used_features)
        train_set = self.merge_predictions(train_set, base_data_train)
        predicted_base_train = self.data_handler.calculate_weighted_aggregations(train_set, self.model_retriever.non_excluded_features, used_features)
        predicted_base_train_df = self.data_handler.construct_final_dataframe(predicted_base_train)
        predicted_base_train_df['dataset'] = 'train'
        step_elapsed = time() - step_time
        logger.info(f"Step - same same for train: {step_elapsed:.2f} seconds")

        
        self.predicted_base_df = predicted_base_df.append(predicted_base_train_df)
        logger.info("Successfully got Predicted and base")
        return self.predicted_base_df.copy()
    

    def get_variable_level_stats(self):
        predicted_base = self.predicted_base_df
        predicted = predicted_base[predicted_base['dataset'] == 'train'][['feature', 'category', 'exposure']]
        relativities = self.get_relativities_df()
        coef_table = self.model_retriever.predictor._clf.coef_table.reset_index()
        coef_table['se_pct'] = coef_table['se']/abs(coef_table['coef'])*100
        features = self.model_retriever.get_features_used_in_modelling()
        
        coef_table_intercept = coef_table[coef_table['index'] == 'intercept']
        coef_table_intercept['feature'] = 'base'
        coef_table_intercept['value'] = 'base'
        coef_table_intercept['exposure'] = 0
        coef_table_intercept['exposure_pct'] = 0
        coef_table_intercept['relativity'] = relativities[relativities['feature'] == 'base']['relativity'].iloc[0]

        variable_stats = coef_table_intercept[['feature', 'value', 'relativity', 'coef', 'se', 'se_pct', 'exposure', 'exposure_pct']]
        
        categorical_features = [feature['variable'] for feature in features if (feature['variableType']=='categorical' and feature['isInModel']==True)]
        
        if len(categorical_features)>0:
        
            predicted_cat = predicted[predicted['feature'].isin(categorical_features)]
            relativities_cat = relativities[relativities['feature'].isin(categorical_features)]
            coef_table_cat = coef_table[(coef_table['index']=='intercept') | (coef_table['index'].str.contains(':'))]

            coef_table_cat[['dummy', 'variable', 'value']] = coef_table_cat['index'].str.split(':', expand=True)
            variable_stats_cat = relativities_cat.merge(coef_table_cat[['variable', 'value', 'coef', 'se', 'se_pct']], how='left', left_on=['feature', 'value'], right_on=['variable', 'value'])

            variable_stats_cat.drop('variable', axis=1, inplace=True)

            predicted_cat['exposure_sum'] = predicted_cat['exposure'].groupby(predicted_cat['feature']).transform('sum')
            predicted_cat['exposure_pct'] = predicted_cat['exposure']/predicted_cat['exposure_sum']*100

            variable_stats_cat = variable_stats_cat.merge(predicted_cat, how='left', left_on=['feature', 'value'], right_on=['feature', 'category'])
            variable_stats_cat.drop(['category', 'exposure_sum'], axis=1, inplace=True)
            variable_stats = variable_stats.append(variable_stats_cat)
            
        numeric_features = [feature['variable'] for feature in features if (feature['variableType']=='numeric' and feature['isInModel']==True)]
        
        if len(numeric_features)>0:
            coef_table_num = coef_table[coef_table['index'].isin(numeric_features)]
            coef_table_num['feature'] = coef_table_num['index']
            coef_table_num['value'] = [self.base_values[feature] for feature in coef_table_num['feature']]
            coef_table_num['exposure'] = 0
            coef_table_num['exposure_pct'] = 0
            coef_table_num['relativity'] = 1

            variable_stats_num = coef_table_num[['feature', 'value', 'relativity', 'coef', 'se', 'se_pct', 'exposure', 'exposure_pct']]
        
            variable_stats = variable_stats.append(variable_stats_num)
        
        return variable_stats
