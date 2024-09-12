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
        logger.info("Computing base values on initation.")
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
        match = re.search(pattern, custom_code)
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
        logger.info("Extracting base levels from original data for features:")
        params = self.model_retriever.predictor.params
        preprocessing_feature = params.preprocessing_params['per_feature']
        logger.info(f"{preprocessing_feature.keys()}.")
        for feature in preprocessing_feature.keys():
            print(feature)
            self.base_values[feature] = self.extract_base_level(preprocessing_feature[feature]['customHandlingCode'])
        logger.info("Base levels extracted")


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
        logger.info("Starting initialize_baseline method")

        logger.debug("Getting the first row of the train set")
        train_row = self.train_set.head(1).copy()
        logger.debug(f"Initial train_row shape: {train_row.shape}")
        logger.debug(f"Initial train_row columns: {train_row.columns}")

        logger.debug("Retrieving used features from model_retriever")
        used_features = self.model_retriever.get_used_features()
        
        logger.info(f"Used features: {used_features}")
#         train_row = train_row[used_features]
        
#         logger.info(f"Filtered train row is : {train_row}")
        logger.info("Setting base values for each feature")
        for feature in used_features:
            logger.debug(f"Setting base value for feature: {feature}")
            base_value = self.base_values[feature]
            train_row[feature] = base_value
            logger.debug(f"Set {feature} to base value: {base_value}")

        logger.debug("Checking for exposure columns")
        if self.model_retriever.exposure_columns is not None:
            logger.info(f"Setting exposure column(s) to 1: {self.model_retriever.exposure_columns}")
            train_row[self.model_retriever.exposure_columns] = 1
            logger.debug(f"Exposure column(s) set to 1")
        else:
            logger.info("No exposure columns to set")

        logger.debug("Final train_row details:")
        logger.debug(f"Shape: {train_row.shape}")
        logger.debug(f"Columns: {train_row.columns}")
        logger.debug(f"Values: \n{train_row.to_dict(orient='records')[0]}")

        logger.info("Successfully completed initialize_baseline method")
        return train_row

    def calculate_baseline_prediction(self, sample_train_row):
        logger.info("Calculating baseline prediction")
        return self.model_retriever.predictor.predict(sample_train_row).iloc[0][0]

    def calculate_relative_predictions(self, sample_train_row, baseline_prediction):
        logger.info("Starting calculate_relative_predictions")
        logger.debug(f"Input parameters: sample_train_row shape: {sample_train_row.shape}, baseline_prediction: {baseline_prediction}")

        self.relativities = {'base': {'base': baseline_prediction}}
        logger.debug(f"Initialized relativities with base: {self.relativities}")
        used_features = self.model_retriever.get_used_features()
        for feature in used_features:
            logger.info(f"Processing feature: {feature}")
            logger.debug(f"Base value for {feature}: {self.base_values[feature]}")

            self.relativities[feature] = {self.base_values[feature]: 1.0}
            logger.debug(f"Initialized relativities for {feature}: {self.relativities[feature]}")

            feature_type = self.model_retriever.features[feature]['type']
            logger.debug(f"Feature type for {feature}: {feature_type}")

            if feature_type == 'CATEGORY':
                logger.info(f"Processing categorical feature: {feature}")
                for modality in self.modalities[feature]:
                    logger.debug(f"Processing modality: {modality} for feature: {feature}")

                    train_row_copy = sample_train_row.copy()
                    train_row_copy[feature] = modality
                    logger.debug(f"Created train_row_copy with {feature} set to {modality}")

                    prediction = self.model_retriever.predictor.predict(train_row_copy).iloc[0][0]
                    logger.debug(f"Prediction for {feature}={modality}: {prediction}")

                    relativity = prediction / baseline_prediction
                    self.relativities[feature][modality] = relativity
                    logger.debug(f"Calculated relativity for {feature}={modality}: {relativity}")

            else:
                logger.info(f"Processing non-categorical feature: {feature}")
                train_row_copy = sample_train_row.copy()
                logger.debug(f"Created train_row_copy for non-categorical feature")

                unique_values = sorted(list(set(self.train_set[feature])))
                logger.debug(f"Unique values for {feature}: {unique_values}")

                for value in unique_values:
                    logger.debug(f"Processing value: {value} for feature: {feature}")

                    train_row_copy[feature] = value
                    logger.debug(f"Set {feature} to {value} in train_row_copy")

                    prediction = self.model_retriever.predictor.predict(train_row_copy).iloc[0][0]
                    logger.debug(f"Prediction for {feature}={value}: {prediction}")

                    relativity = prediction / baseline_prediction
                    self.relativities[feature][value] = relativity
                    logger.debug(f"Calculated relativity for {feature}={value}: {relativity}")

        logger.info("Finished calculate_relative_predictions")
        logger.debug(f"Final relativities: {self.relativities}")

    def construct_relativities_df(self):
        logger.info("constructing relativites DF")
        rel_df = pd.DataFrame(columns=['feature', 'value', 'relativity'])
        for feature, values in self.relativities.items():
            for value, relativity in values.items():
                rel_df = rel_df.append({'feature': feature, 'value': value, 'relativity': relativity}, ignore_index=True)
        rel_df.coluns = ['variable', 'category', 'relativity']
        return rel_df

    def apply_weights_to_data(self, test_set):
#         used_features = list(self.base_values.keys())
        used_features = self.model_retriever.get_used_features()
        print(f"Using feature list of {used_features}")
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
        logger.info("Starting compute_base_predictions_new")
        step_time = time()
        base_data = dict()
        logger.debug(f"Initialized empty base_data dictionary")

        for feature in used_features:
            logger.debug(f"Starting loop for feature: {feature}")
            logger.debug(f"Current used_features: {used_features}")

            logger.debug(f"Creating a copy of test_set for feature: {feature}")
            copy_test_df = test_set.copy()
            logger.debug(f"Shape of copy_test_df: {copy_test_df.shape}")

            logger.debug(f"Grouping copy_test_df by {feature} and taking first row of each group")
            copy_test_df = copy_test_df.groupby(feature, as_index=False).first()
            logger.debug(f"Shape of grouped copy_test_df: {copy_test_df.shape}")

            logger.debug(f"Setting exposure column(s) to 1")
            copy_test_df[self.model_retriever.exposure_columns] = 1
            logger.debug(f"Sample of copy_test_df after setting exposure: {copy_test_df.head()}")

            for other_feature in [col for col in used_features if col != feature]:
                logger.debug(f"Setting base value for other feature: {other_feature}")
                copy_test_df[other_feature] = self.base_values[other_feature]
                logger.debug(f"Set {other_feature} to {self.base_values[other_feature]}")

            logger.debug(f"Making predictions for feature: {feature}")
            predictions = self.model_retriever.predictor.predict(copy_test_df)
            logger.debug(f"Shape of predictions: {predictions.shape}")

            logger.debug(f"Creating DataFrame for base_data[{feature}]")
            base_data[feature] = pd.DataFrame(data={('base_' + feature): predictions['prediction'], feature: copy_test_df[feature]})
            logger.debug(f"Shape of base_data[{feature}]: {base_data[feature].shape}")

            logger.debug(f"Completed loop for feature: {feature}")

        step_elapsed = time() - step_time
        logger.info(f"compute_base_predictions_new completed in {step_elapsed:.2f} seconds")
        logger.info(f"Successfully computed base predictions for features: {used_features}")
        logger.debug(f"Final base_data keys: {base_data.keys()}")
        return base_data

    def merge_predictions(self, test_set, base_data):
        logger.info("Merging Base predictions")
        for feature in base_data.keys():
            test_set = pd.merge(test_set, base_data[feature], how='left', on=feature)
        logger.info("Successfully Merged Base predictions")
        return test_set


    def get_formated_predicted_base(self):
        logger.info("Getting formatted and predicted base")
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
        logger.info("Successfully got formatted and predicted base")
        return df
    
    def process_dataset(self, dataset, dataset_name):
        logger.info(f"Processing dataset {dataset_name}")
        used_features = self.model_retriever.get_used_features()
        base_data = self.compute_base_predictions_new(dataset, used_features)
        dataset = self.merge_predictions(dataset, base_data)
        predicted_base = self.data_handler.calculate_weighted_aggregations(dataset, self.model_retriever.non_excluded_features, used_features)
        predicted_base_df = self.data_handler.construct_final_dataframe(predicted_base)
        predicted_base_df['dataset'] = dataset_name
        logger.info(f"Processed dataset {dataset_name}")
        return predicted_base_df
    
    
    def get_predicted_and_base(self, nb_bins_numerical=100000):
        logger.info("Getting Predicted and base")
        
        self.compute_base_values()
        
        test_predictions = self.process_dataset(self.test_set, 'test')
        train_predictions = self.process_dataset(self.train_set, 'train')

        self.predicted_base_df = train_predictions.append(test_predictions)
        

        logger.info("Successfully got Predicted and base")
        return self.predicted_base_df.copy()
    


