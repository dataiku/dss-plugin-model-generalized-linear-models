import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from glm_handler.dku_utils import extract_active_fullModelId
import logging
from backend.logging_settings import logger
from glm_handler.dku_relativities_handler import RelativitiesHandler
import time

class ModelHandler:
    """
    A class to handle interactions with a Dataiku model.

    Attributes:
        model_id (str): The ID of the model.
        model (dataiku.Model): The Dataiku model object.
        full_model_id (str): The full model ID of the active model version.
        model_info_handler (PredictionModelInformationHandler): Handler for model information.
    """

    def __init__(self, model_id, data_handler):
        """
        Initializes the ModelHandler with a specific model ID.

        Args:
            model_id (str): The ID of the model to handle.
        """
        self.model_id = model_id
        self.model = dataiku.Model(model_id)
        self.data_handler = data_handler
        self.base_values = {}
        self.modalities = {}
        
    
    def get_coefficients(self):
        """
        Retrieves the coefficients of the model predictor.

        Returns:
            dict: A dictionary mapping variable names to their coefficients.
        """
        coefficients = self.predictor._model.clf.coef_
        variable_names = self.predictor._model.clf.column_labels
        return dict(zip(variable_names, coefficients))

    
    def update_active_version(self):
        
        start_time = time.time()  # Start the timer for the whole method
        # Step 1: Initialize model
        step_start = time.time()
        list_version = self.model.list_versions()
        print("Step 1 duration:", time.time() - step_start)

        # Step 2: Extract active fullModelId and print it
        step_start = time.time()
        self.full_model_id = extract_active_fullModelId(list_version)
        print("Step 2 duration:", time.time() - step_start)

        # Step 3: Setup model information handler
        step_start = time.time()
        self.model_info_handler = PredictionModelInformationHandler.from_full_model_id(self.full_model_id)
        print("Step 3 duration:", time.time() - step_start)

        # Step 4: Get predictor and target variable
        step_start = time.time()
        self.predictor = self.model_info_handler.get_predictor()
        self.target = self.model_info_handler.get_target_variable()
        print("Step 4 duration:", time.time() - step_start)

        # Step 5: Initialize base values and modalities dictionaries
        step_start = time.time()
        self.base_values = dict()
        self.modalities = dict()
        print("Step 5 duration:", time.time() - step_start)

        # Step 6: Compute features
        step_start = time.time()
        self.compute_features()
        print("Step 6 duration:", time.time() - step_start)

        # Step 7: Compute base values
        step_start = time.time()
        self.compute_base_values()
        print("Step 7 duration:", time.time() - step_start)

        # Step 8: Initialize relativities handler
        step_start = time.time()
        self.relativities_handler = RelativitiesHandler(self.model_info_handler)
        print("Step 8 duration:", time.time() - step_start)

        # Print total duration
        print("Total method duration:", time.time() - start_time)

    def get_model_versions(self):
        versions = self.model.list_versions()
        fmi_name = {version['snippet']['fullModelId']: version['snippet']['userMeta']['name'] for version in versions}
        return fmi_name
    
    def get_features(self):
        return [{'variable': feature, 
          'isInModel': self.features[feature]['role']=='INPUT', 
          'variableType': 'categorical' if self.features[feature]['type'] == 'CATEGORY' else 'numeric'} for feature in self.non_excluded_features]
    
    def compute_features(self):
        """ Main method to compute feature configurations. """
        self.initialize_feature_variables()
        self.compute_column_roles()
        self.filter_features()

    def initialize_feature_variables(self):
        """ Initializes basic variables related to features. """
        self.exposure = None
        self.features = self.model_info_handler.get_per_feature()

    def compute_column_roles(self):
        """ Computes special columns like exposure and offset columns from modeling params. """
        modeling_params = self.model_info_handler.get_modeling_params()
        self.offset_columns = modeling_params['plugin_python_grid']['params']['offset_columns']
        self.exposure_columns = modeling_params['plugin_python_grid']['params']['exposure_columns']
        if len(self.exposure_columns) > 0:
            self.exposure = self.exposure_columns[0]  # assumes there is only one exposure column

    def filter_features(self):
        """ Filters features based on their importance and role in the model. """
        important_columns = self.offset_columns + self.exposure_columns + [self.target]
        self.non_excluded_features = [feature for feature in self.features.keys() if feature not in important_columns]
        self.used_features = [feature for feature in self.non_excluded_features if self.features[feature]['role'] == 'INPUT']
        self.candidate_features = [feature for feature in self.non_excluded_features if self.features[feature]['role'] == 'REJECT']

    def compute_base_values(self):
        """ Main method to initialize and compute base values. """
        self.handle_preprocessing()
        self.compute_numerical_features()


    def handle_preprocessing(self):
        """ Processes each step in the preprocessing pipeline. """
        preprocessing = self.predictor.get_preprocessing()
        for step in preprocessing.pipeline.steps:
            self.process_preprocessing_step(step)

    def process_preprocessing_step(self, step):
        """ Processes a single preprocessing step to extract base values and modalities. """
        try:
            self.base_values[step.input_col] = step.processor.mode_column
            self.modalities[step.input_col] = step.processor.modalities
        except AttributeError:
            pass

    def compute_numerical_features(self):
        """ Computes base values for numerical features not handled in preprocessing. """
        train_set = self.model_info_handler.get_train_df()[0].copy()
        for feature in self.used_features:
            if feature not in self.base_values:
                self.compute_base_for_feature(feature, train_set)

    def compute_base_for_feature(self, feature, train_set):
        """ Computes base value for a single feature based on its type and rescaling. """
        if self.features[feature]['type'] == 'NUMERIC' and self.features[feature]['rescaling'] == 'NONE':
            self.compute_base_for_numeric_feature(feature, train_set)
        else:
            raise Exception("feature should be handled numerically without rescaling or categorically with the custom preprocessor")

    def compute_base_for_numeric_feature(self, feature, train_set):
        """ Computes base values for numeric features without rescaling. """
        if self.exposure is not None:
            self.base_values[feature] = (train_set[feature] * train_set[self.exposure]).sum() / train_set[self.exposure].sum()
        else:
            self.base_values[feature] = train_set[feature].mean()
        self.modalities[feature] = {'min': train_set[feature].min(), 'max': train_set[feature].max()}

    def get_relativities_df(self):
        sample_train_row = self.initialize_baseline()
        baseline_prediction = self.calculate_baseline_prediction(sample_train_row)
        self.calculate_relative_predictions(sample_train_row, baseline_prediction)
        return self.construct_relativities_df()

    def initialize_baseline(self):
        train_row = self.model_info_handler.get_train_df()[0].head(1).copy()
        for feature in self.base_values.keys():
            train_row[feature] = self.base_values[feature]
        if self.exposure is not None:
            train_row[self.exposure] = 1
        return train_row

    def calculate_baseline_prediction(self, sample_train_row):
        return self.predictor.predict(sample_train_row).iloc[0][0]

    def calculate_relative_predictions(self, sample_train_row, baseline_prediction):
        self.relativities = {'base': {'base': baseline_prediction}}
        for feature in self.base_values.keys():
            self.relativities[feature] = {self.base_values[feature]: 1.0}
            if self.features[feature]['type'] == 'CATEGORY':    
                for modality in self.modalities[feature]:
                    train_row_copy = sample_train_row.copy()
                    train_row_copy[feature] = modality
                    prediction = self.predictor.predict(train_row_copy).iloc[0][0]
                    self.relativities[feature][modality] = prediction / baseline_prediction
            else:
                train_row_copy = sample_train_row.copy()
                min_value, max_value = self.modalities[feature]['min'], self.modalities[feature]['max']
                for value in np.linspace(min_value, max_value, 10):
                    train_row_copy[feature] = value
                    prediction = self.predictor.predict(train_row_copy).iloc[0][0]
                    self.relativities[feature][value] = prediction / baseline_prediction

    def construct_relativities_df(self):
        rel_df = pd.DataFrame(columns=['feature', 'value', 'relativity'])
        for feature, values in self.relativities.items():
            for value, relativity in values.items():
                rel_df = rel_df.append({'feature': feature, 'value': value, 'relativity': relativity}, ignore_index=True)
        #rel_df = rel_df.append({'feature': 'base', 'value': 'base', 'relativity': self.relativities['base']['base']}, ignore_index=True)
        rel_df.columns = ['variable', 'category', 'relativity']
        return rel_df

    def get_predicted_and_base_feature(self, feature, nb_bins_numerical=100000, class_map=None):
        test_set = self.extract_test_set_predictions()
        self.apply_weights_to_data(test_set)
        base_predictions = self.compute_base_predictions(test_set, feature, class_map)
        predicted_base_df = self.prepare_final_data(test_set, feature, nb_bins_numerical, base_predictions)
        return predicted_base_df

    def extract_test_set_predictions(self):
        test_set = self.model_info_handler.get_test_df()[0].copy()
        predicted = self.predictor.predict(test_set)
        test_set['predicted'] = predicted
        return test_set

    def apply_weights_to_data(self, test_set):
        used_features = list(self.base_values.keys())
        if self.exposure is None:
            test_set['weight'] = 1
        else:
            test_set['weight'] = test_set[self.exposure]
        test_set['weighted_target'] = test_set[self.target] * test_set['weight']
        test_set['weighted_predicted'] = test_set['predicted'] * test_set['weight']

    def compute_base_predictions(self, test_set, feature, class_map):
        base_data = {}
        copy_test_df = test_set.copy()
        used_features = list(self.base_values.keys())
        for other_feature in [col for col in used_features if col != feature]:
            copy_test_df[other_feature] = self.base_values[other_feature]
        predictions = self.predictor.predict(copy_test_df)
        if class_map is not None:
            base_data[feature] = pd.Series([class_map[pred] for pred in predictions['prediction']])
        else:
            base_data[feature] = predictions
        base_predictions = pd.concat([base_data[feature]], axis=1)
        base_predictions.columns = ['base_' + feature]
        return base_predictions

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


    def prepare_test_set(self):
        test_set = self.model_info_handler.get_test_df()[0].copy()
        predicted = self.predictor.predict(test_set)
        test_set['predicted'] = predicted
        test_set['weight'] = 1 if self.exposure is None else test_set[self.exposure]
        test_set['weighted_target'] = test_set[self.target] * test_set['weight']
        test_set['weighted_predicted'] = test_set['predicted'] * test_set['weight']
        return test_set

    def compute_base_predictions(self, test_set, used_features, class_map=None):
        base_data = dict()
        for feature in self.non_excluded_features:
            copy_test_df = test_set.copy()
            for other_feature in [col for col in used_features if col != feature]:
                copy_test_df[other_feature] = self.base_values[other_feature]
            predictions = self.predictor.predict(copy_test_df)
            if class_map is not None:
                base_data[feature] = pd.Series([class_map[pred] for pred in predictions['prediction']])
            else:
                base_data[feature] = predictions
        return base_data

    def merge_predictions(self, test_set, base_data):
        base_predictions = pd.concat([base_data[feature] for feature in base_data], axis=1)
        base_predictions.columns = ['base_' + feature for feature in self.non_excluded_features]
        return pd.concat([test_set, base_predictions], axis=1)


    def get_predicted_and_base(self, nb_bins_numerical=100000, class_map=None):
        self.compute_base_values()
        test_set = self.prepare_test_set()
        used_features = list(self.base_values.keys())
        base_data = self.compute_base_predictions(test_set, used_features, class_map)
        test_set = self.merge_predictions(test_set, base_data)
        test_set = self.data_handler.bin_numeric_columns(test_set, nb_bins_numerical,self.features, self.non_excluded_features)
        predicted_base = self.data_handler.calculate_weighted_aggregations(test_set, self.non_excluded_features)
        predicted_base_df = self.data_handler.construct_final_dataframe(predicted_base)
        self.predicted_base_df = predicted_base_df
        return predicted_base_df


    def get_model_predictions_on_train(self):
        """
        Generates model predictions on the training dataset.

        Returns:
            pd.DataFrame: A DataFrame of the training dataset with an additional column for predictions.
        """
        train_set = self.model_info_handler.get_train_df()[0].copy()
        predicted = self.predictor.predict(train_set)
        train_set['prediction'] = predicted
        
        return train_set
    
    def get_lift_chart(self, nb_bins):
        """
        Calculates and returns the lift chart data for the model on the training set,
        divided into the specified number of bins.

        Args:
            nb_bins (int): The number of bins to divide the data into for the lift chart.

        Returns:
            pd.DataFrame: The aggregated lift chart data with observed and predicted metrics.
        """
        train_set = self.get_model_predictions_on_train()
        train_set_df = pd.DataFrame(train_set)
        
        tempdata = self.data_handler.sort_and_cumsum_exposure(train_set_df, self.exposure)
        binned_data = self.data_handler.bin_data(tempdata, nb_bins)
        
        new_data = train_set.join(binned_data[['bin']], how='inner')
        lift_chart_data = self.data_handler.aggregate_metrics_by_bin(new_data, self.exposure, self.target)
        lift_chart_data.columns = ['Category', 'Value', 'observedAverage', 'fittedAverage']
        return lift_chart_data

    def get_variable_level_stats(self):
        print('Setting up variable level stats')
        
        predicted = self.get_predicted_and_base()[['feature', 'category', 'exposure']]

        relativities = self.get_relativities_df()
        
        coef_table = self.predictor._clf.coef_table.reset_index()
        coef_table.rename({'index':'not_index'},axis=1,inplace=True)
        split_columns = coef_table['not_index'].str.split(':', expand=True)
        coef_table['dummy'],coef_table['variable']   = split_columns[0],split_columns[1],split_columns[2] 
        coef_table['se_pct'] = coef_table['se']/abs(coef_table['coef'])*100
        print(f"coef_table is {coef_table}")
        print(f"relativites is {relativities}")
        variable_stats = relativities.merge(coef_table[['variable', 'value', 'coef', 'se', 'se_pct']], how='left', left_on=['feature', 'value'], right_on=['variable', 'value'])
        variable_stats.drop('variable', axis=1, inplace=True)
        print(f"variables stats are {variable_stats}")
        predicted['exposure_sum'] = predicted['exposure'].groupby(predicted['feature']).transform('sum')
        predicted['exposure_pct'] = predicted['exposure']/predicted['exposure_sum']*100
        
        variable_level_stats = variable_stats.merge(predicted, how='left', left_on=['feature', 'value'], right_on=['feature', 'category'])
        variable_level_stats.drop(['category', 'exposure_sum'], axis=1, inplace=True)
        variable_level_stats.columns = ['variable', 'value', 'relativity', 'coefficient', 'standard_error', 'standard_error_pct', 'weight', 'weight_pct']
        variable_level_stats.fillna(0, inplace=True)
        variable_level_stats.replace([np.inf, -np.inf], 0, inplace=True)

        
        return variable_level_stats
        
    def get_link_function(self):
        """
        Retrieves the link function of the original model as a statsmodel object
        """
        return self.predictor._model.clf.get_link_function()
    
    def get_dataframe(self, dataset_type='test'):
        """
        Retrieves the specified dataset as a DataFrame.

        Args:
            dataset_type (str, optional): The type of dataset to retrieve ('test', 'train', or 'full'). Defaults to 'test'.

        Returns:
            pd.DataFrame: The requested dataset.

        Raises:
            ValueError: If an invalid dataset type is provided.
        """
        if dataset_type == 'test':
            return self.model_info_handler.get_test_df()[0]
        elif dataset_type == 'train':
            return self.model_info_handler.get_train_df()[0]
        elif dataset_type == 'full':
            return self.model_info_handler.get_full_df()[0]
        else:
            raise ValueError("Invalid dataset type")

