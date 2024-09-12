import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from glm_handler.dku_utils import extract_active_fullModelId
from logging_assist.logging import logger
from time import time
import re

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
    
    def get_base_values(self):
        logger.info(f"Getting base values")
        return self.base_values
    
    def compute_base_values(self):
        """
        Main method to initialize and compute base values.
        """
        logger.info("Computing base values.")
        step_time = time()
        step_elapsed = time() - step_time
        print("Handle preprocessing")
        self.handle_preprocessing()
        self.handle_modalities()
        #self.compute_numerical_features()
        logger.info(f"Compute base values: {step_elapsed:.2f} seconds")

    def handle_modalities(self):
        """
        Extracts modalities from train set
        """
        for feature in self.base_values.keys():
            self.modalities[feature] = self.train_set[feature].unique()

    def extract_base_level(self, custom_code):
        """
        Extracts Base Level from preprocessing custom code
        """
        base_level = None
        pattern = r'self\.mode_column\s*=\s*["\']([^"\']+)["\']'
        # Search for the pattern in the code string
        logger.debug("Custom Code is {custom_code}")
        match = re.search(pattern, custom_code)
        logger.debug(f"Match is {match}")
        
        # Extract and print the matched value
        if match:
            base_level = match.group(1)
        else:
            pattern = r'self\.mode_column\s*=\s*(\d+)'
            match = re.search(pattern, custom_code)
            if match:
                base_level = int(match.group(1))
        logger.debug(f"returning base_level {base_level}")
        return base_level

    def handle_preprocessing(self):
        """
        Processes each step in the preprocessing pipeline.
        """
        logger.info("Handling preprocessing steps.")
        params = self.model_retriever.predictor.params
        preprocessing_feature = params.preprocessing_params['per_feature']
        for feature in preprocessing_feature.keys():
            print(feature)
            self.base_values[feature] = self.extract_base_level(preprocessing_feature[feature]['customHandlingCode'])
        logger.info("Preprocessing handled.")


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

        logger.info(f"Relativities DataFrame computed")
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
        print(f"train set columns are {train_set.columns}")
        print(f"self.model_retriever.target_column {self.model_retriever.target_column}")
        print(f"self.model_retriever.exposure_column {self.model_retriever.exposure_columns}")
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
        step_time = time()
        base_data = dict()
        for feature in used_features:
            copy_test_df = test_set.copy()
            copy_test_df = copy_test_df.groupby(feature, as_index=False).first()
            copy_test_df[self.model_retriever.exposure_columns] = 1
            for other_feature in [col for col in used_features if col != feature]:
                copy_test_df[other_feature] = self.base_values[other_feature]
            predictions = self.model_retriever.predictor.predict(copy_test_df)
            base_data[feature] = pd.DataFrame(data={('base_' + feature): predictions['prediction'], feature: copy_test_df[feature]})
        step_elapsed = time() - step_time
        logger.info(f"Step - compute base predictions: {step_elapsed:.2f} seconds")
        return base_data

    def merge_predictions(self, test_set, base_data):
        logger.info("Merging Base predictions")
        for feature in base_data.keys():
            test_set = pd.merge(test_set, base_data[feature], how='left', on=feature)
        logger.info("Successfully Merged Base predictions")
        return test_set


    def get_formated_predicted_base(self):
        self.get_predicted_and_base()
        df = self.predicted_base_df.copy()
        df.columns = ['definingVariable', 
                                             'Category', 
                                             'observedAverage', 
                                             'fittedAverage', 'Value', 'baseLevelPrediction', 'dataset']
        df['observedAverage'] = [float('%s' % float('%.3g' % x)) for x in  df['observedAverage']]
        df['fittedAverage'] = [float('%s' % float('%.3g' % x)) for x in df['fittedAverage']]
        df['Value'] = [float('%s' % float('%.3g' % x)) for x in  df['Value']]
        df['baseLevelPrediction'] = [float('%s' % float('%.3g' % x)) for x in  df['baseLevelPrediction']]
        return df
    
    def process_dataset(self, dataset, dataset_name):
        logger.info("Processing dataset {dataset_name}")
        
        used_features = list(self.base_values.keys())
        base_data = self.compute_base_predictions_new(dataset, used_features)
        dataset = self.merge_predictions(dataset, base_data)
        predicted_base = self.data_handler.calculate_weighted_aggregations(dataset, self.model_retriever.non_excluded_features, used_features)
        predicted_base_df = self.data_handler.construct_final_dataframe(predicted_base)
        predicted_base_df['dataset'] = dataset_name
        logger.info("Processed dataset {dataset_name}")
        return predicted_base_df
    
    
    def get_predicted_and_base(self, nb_bins_numerical=100000):
        logger.info("Getting Predicted and base")
        
        self.compute_base_values()
        
        test_predictions = self.process_dataset(self.test_set, 'test')
        train_predictions = self.process_dataset(self.train_set, 'train')

        self.predicted_base_df = train_predictions.append(test_predictions)
        

        logger.info("Successfully got Predicted and base")
        return self.predicted_base_df.copy()
    


