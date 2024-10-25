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
        self.variable_types = {}
        self.model_retriever = model_retriever
        try:
            self.train_set = self.prepare_dataset('train')
            self.test_set = self.prepare_dataset('test')
            self.compute_base_values()
            logger.info("Relativities ModelHandler initialized.")
            logger.info(f"length of train set is {len(self.train_set)}")
        except Exception as e:
            logger.error(f"Error initializing RelativitiesCalculator: {e}")
            self.train_set = None
            self.test_set = None
        
    def compute_base_values(self):
        logger.info("Computing base values on initiation.")
        params = self.model_retriever.predictor.params
        preprocessing_features = params.preprocessing_params['per_feature']

        for feature, config in preprocessing_features.items():
            self.base_values[feature] = self.extract_base_level(config['customHandlingCode'])
            self.modalities[feature] = self.train_set[feature].unique()
            self.variable_types[feature] = config['type']

        logger.info("Base values computed and modalities extracted.")

    def get_base_values(self):
        logger.info(f"Getting base values")
        return self.base_values

    def extract_base_level(self, custom_code):
        """
        Extracts Base Level from preprocessing custom code
        """
        base_level = None
        pattern = r'self\.mode_column\s*=\s*["\']([^"\']+)["\']'
        # Search for the pattern in the code string
        match = re.search(pattern, custom_code)
        if match:
            base_level = match.group(1)
        else:
            pattern = r'self\.mode_column\s*=\s*(\d+)'
            match = re.search(pattern, custom_code)
            if match:
                base_level = int(match.group(1))
        logger.debug(f"returning base_level {base_level}")
        return base_level

    def initialize_baseline(self):
        logger.info("Starting initialize_baseline method")
        train_row = self.train_set.head(1).copy()
        used_features = self.model_retriever.get_used_features()
        logger.info(f"Used features: {used_features}")
        
        for feature in used_features:
            base_value = self.base_values[feature]
            train_row[feature] = base_value

        if self.model_retriever.exposure_columns is not None:
            train_row[self.model_retriever.exposure_columns] = 1
            logger.debug(f"Exposure column(s) set to 1")
        else:
            logger.info("No exposure columns to set")

        logger.info("Successfully completed initialize_baseline method")
        return train_row

    def calculate_baseline_prediction(self, sample_train_row):
        logger.info("Calculating baseline prediction")
        return self.model_retriever.predictor.predict(sample_train_row).iloc[0][0]

    def construct_relativities_df(self):
        logger.info("constructing relativites DF")
        rel_df = pd.DataFrame(columns=['feature', 'value', 'relativity'])
        for feature, values in self.relativities.items():
            for value, relativity in values.items():
                rel_df = rel_df.append({'feature': feature, 'value': value, 'relativity': relativity}, ignore_index=True)
        rel_df.coluns = ['variable', 'category', 'relativity']
        return rel_df
    
    def get_relativities_df(self):
        """
        Computes and returns the relativities DataFrame for the model.
        Returns:
            pd.DataFrame: The relativities DataFrame.
        """
        logger.info("Computing relativities DataFrame.")
        sample_train_row = self.initialize_baseline()
        baseline_prediction = self.calculate_baseline_prediction(sample_train_row)

        self.relativities = {'base': {'base': baseline_prediction}}
        used_features = self.model_retriever.get_used_features()

        for feature in used_features:
            feature_type = self.model_retriever.features[feature]['type']
            base_value = self.base_values[feature]
            self.relativities[feature] = {base_value: 1.0}
            train_row_copy = sample_train_row.copy()

            values_to_process = (self.modalities[feature] if feature_type == 'CATEGORY' 
                                 else sorted(set(self.train_set[feature])))

            for value in values_to_process:
                train_row_copy[feature] = value
                prediction = self.model_retriever.predictor.predict(train_row_copy).iloc[0][0]
                relativity = prediction / baseline_prediction
                self.relativities[feature][value] = relativity

        relativities_df = self.construct_relativities_df()
        logger.info("Relativities DataFrame computed")
        return relativities_df

    def apply_weights_to_data_deprecated(self, test_set):
#         used_features = list(self.base_values.keys())
        used_features = self.model_retriever.get_used_features()
        print(f"Using feature list of {used_features}")
        if self.model_retriever.exposure_columns is None:
            test_set['weight'] = 1
        else:
            test_set['weight'] = test_set[self.model_retriever.exposure]
        test_set['weighted_target'] = test_set[self.model_retriever.target_columns] * test_set['weight']
        test_set['weighted_predicted'] = test_set['predicted'] * test_set['weight']

    def prepare_dataset(self, dataset_type='train'):
        """
        Prepares and returns either the training or test dataset.

        Args:
            dataset_type (str): Either 'train' or 'test'. Defaults to 'train'.

        Returns:
            pd.DataFrame: The prepared dataset.
        """
        logger.info(f"Preparing {dataset_type} dataset.")

        if dataset_type == 'train':
            dataset = self.model_retriever.model_info_handler.get_train_df()[0].copy()
        elif dataset_type == 'test':
            dataset = self.model_retriever.model_info_handler.get_test_df()[0].copy()
        else:
            raise ValueError("dataset_type must be either 'train' or 'test'")

        predicted = self.model_retriever.predictor.predict(dataset)
        dataset['predicted'] = predicted
        dataset['weight'] = 1 if self.model_retriever.exposure_columns is None else dataset[self.model_retriever.exposure_columns]

        dataset['weighted_target'] = dataset[self.model_retriever.target_column]
        dataset['weighted_predicted'] = dataset['predicted']

        logger.info(f"{dataset_type.capitalize()} dataset prepared: {dataset.shape}")
        return dataset
    
    def compute_base_predictions_new(self, test_set, used_features):
        logger.info(f"Starting compute_base_predictions_new for {used_features}")
        base_data = {}
        copy_test_df = test_set.copy()
        copy_test_df[self.model_retriever.exposure_columns] = 1

        for feature in used_features:
            feature_df = copy_test_df.groupby(feature, as_index=False).first()

            for other_feature in used_features:
                if other_feature != feature:
                    feature_df[other_feature] = self.base_values[other_feature]

            predictions = self.model_retriever.predictor.predict(feature_df)
            base_data[feature] = pd.DataFrame({
                f'base_{feature}': predictions['prediction'],
                feature: feature_df[feature]
            })

        logger.info("Finished compute_base_predictions_new")
        return base_data

    def get_formated_predicted_base(self):
        logger.info("Getting formatted and predicted base")
        self.get_predicted_and_base()
        df = self.predicted_base_df.copy()
        df.columns = ['definingVariable', 
                     'Category', 
                     'observedAverage', 
                     'fittedAverage', 'Value', 'baseLevelPrediction', 'dataset']
        logger.info("Successfully got formatted and predicted base")
        return df
    
    def process_dataset_old(self, dataset, dataset_name):
        logger.info(f"Processing dataset {dataset_name}")
        used_features = self.model_retriever.get_used_features()
        base_data = self.compute_base_predictions_new(dataset, used_features)

        # Merge all base_data at once
        dataset = pd.merge(dataset, pd.concat(base_data.values()), on=used_features)

        predicted_base = self.data_handler.calculate_weighted_aggregations(
            dataset, 
            self.model_retriever.non_excluded_features, 
            used_features
        )
        predicted_base_df = self.data_handler.construct_final_dataframe(predicted_base)
        predicted_base_df['dataset'] = dataset_name

        logger.info(f"Processed dataset {dataset_name}")
        return predicted_base_df
    
    def merge_predictions(self, test_set, base_data):
        logger.info("Merging Base predictions")
        for feature in base_data.keys():
            test_set = pd.merge(test_set, base_data[feature], how='left', on=feature)
        logger.info("Successfully Merged Base predictions")
        return test_set
    
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
        categorical_variables = [variable for variable in self.variable_types.keys() if self.variable_types[variable] == 'CATEGORY']
        self.predicted_base_df['category'] = [str(category) if variable in categorical_variables else category for category, variable in zip(self.predicted_base_df['category'], self.predicted_base_df['feature'])]
        logger.info("Successfully got Predicted and base")
        return self.predicted_base_df.copy()
    


