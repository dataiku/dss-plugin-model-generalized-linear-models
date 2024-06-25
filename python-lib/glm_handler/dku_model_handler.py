import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from glm_handler.dku_utils import extract_active_fullModelId
from logging_assist.logging import logger
from glm_handler.dku_relativities_handler import RelativitiesHandler
from time import time

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
        
        self.model = dataiku.Model(self.model_id)
        self.full_model_id = extract_active_fullModelId(self.model.list_versions())
        self.model_info_handler = PredictionModelInformationHandler.from_full_model_id(self.full_model_id)
        self.predictor = self.model_info_handler.get_predictor()
        self.target = self.model_info_handler.get_target_variable()
        self.base_values = dict()
        self.modalities = dict()
        self.compute_features()
        self.train_set = self.prepare_train_set()
        self.test_set = self.prepare_test_set()
        self.compute_base_values()
        self.relativities_handler = RelativitiesHandler(self.model_info_handler)
        
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
        for feature in self.used_features:
            if feature not in self.base_values:
                self.compute_base_for_feature(feature, self.train_set)

    def compute_base_for_feature(self, feature, train_set):
        """ Computes base value for a single feature based on its type and rescaling. """
        if self.features[feature]['type'] == 'NUMERIC' and self.features[feature]['rescaling'] == 'NONE':
            self.compute_base_for_numeric_feature(feature, train_set)
        else:
            raise Exception("feature should be handled numerically without rescaling or categorically with the custom preprocessor")

    def compute_base_for_numeric_feature(self, feature, train_set):
        """ Computes base values for numeric features without rescaling. """
        if self.exposure is not None:
            self.base_values[feature] = float('%s' % float('%.3g' % ((train_set[feature] * train_set[self.exposure]).sum() / train_set[self.exposure].sum())))
        else:
            self.base_values[feature] = float('%s' % float('%.3g' % train_set[feature].mean()))
        self.modalities[feature] = {'min': train_set[feature].min(), 'max': train_set[feature].max()}

    def get_relativities_df(self):
        sample_train_row = self.initialize_baseline()
        baseline_prediction = self.calculate_baseline_prediction(sample_train_row)
        self.calculate_relative_predictions(sample_train_row, baseline_prediction)
        return self.construct_relativities_df()

    def initialize_baseline(self):
        train_row = self.train_set.head(1).copy()
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
                unique_values = sorted(list(set(self.train_set[feature])))
                for value in unique_values:
                    train_row_copy[feature] = value
                    prediction = self.predictor.predict(train_row_copy).iloc[0][0]
                    self.relativities[feature][value] = prediction / baseline_prediction

    def construct_relativities_df(self):
        rel_df = pd.DataFrame(columns=['feature', 'value', 'relativity'])
        for feature, values in self.relativities.items():
            for value, relativity in values.items():
                rel_df = rel_df.append({'feature': feature, 'value': value, 'relativity': relativity}, ignore_index=True)
        rel_df.coluns = ['variable', 'category', 'relativity']
        return rel_df

    def apply_weights_to_data(self, test_set):
        used_features = list(self.base_values.keys())
        if self.exposure is None:
            test_set['weight'] = 1
        else:
            test_set['weight'] = test_set[self.exposure]
        test_set['weighted_target'] = test_set[self.target] * test_set['weight']
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


    def prepare_test_set(self):
        test_set = self.model_info_handler.get_test_df()[0].copy()
        predicted = self.predictor.predict(test_set)
        test_set['predicted'] = predicted
        test_set['weight'] = 1 if self.exposure is None else test_set[self.exposure]
        test_set['weighted_target'] = test_set[self.target] * test_set['weight']
        test_set['weighted_predicted'] = test_set['predicted'] * test_set['weight']
        return test_set
    
    def prepare_train_set(self):
        train_set = self.model_info_handler.get_train_df()[0].copy()
        predicted = self.predictor.predict(train_set)
        train_set['predicted'] = predicted
        train_set['weight'] = 1 if self.exposure is None else train_set[self.exposure]
        train_set['weighted_target'] = train_set[self.target] * train_set['weight']
        train_set['weighted_predicted'] = train_set['predicted'] * train_set['weight']
        return train_set

    def compute_base_predictions(self, test_set, used_features):
        base_data = dict()
        for feature in self.non_excluded_features:
            copy_test_df = test_set.copy()
            for other_feature in [col for col in used_features if col != feature]:
                copy_test_df[other_feature] = self.base_values[other_feature]
            predictions = self.predictor.predict(copy_test_df)
            base_data[feature] = predictions
        return base_data
    
    def compute_base_predictions_new(self, test_set, used_features):
        base_data = dict()
        for feature in used_features:
            copy_test_df = test_set.copy()
            copy_test_df = copy_test_df.groupby(feature, as_index=False).first()
            copy_test_df[self.exposure] = 1
            for other_feature in [col for col in used_features if col != feature]:
                copy_test_df[other_feature] = self.base_values[other_feature]
            predictions = self.predictor.predict(copy_test_df)
            base_data[feature] = pd.DataFrame(data={('base_' + feature): predictions['prediction'], feature: copy_test_df[feature]})
        return base_data

    def merge_predictions(self, test_set, base_data):
        print(base_data)
        for feature in base_data.keys():
            test_set = pd.merge(test_set, base_data[feature], how='left', on=feature)
        return test_set


    def get_predicted_and_base(self, nb_bins_numerical=100000):
        step_time = time()
        self.compute_base_values()
        step_elapsed = time() - step_time
        logger.info(f"Step - Compute base values: {step_elapsed:.2f} seconds")
        
        step_time = time()
        test_set = self.test_set
        train_set = self.train_set
        used_features = list(self.base_values.keys())
        step_elapsed = time() - step_time
        logger.info(f"Step - Get datasets: {step_elapsed:.2f} seconds")
        
        step_time = time()
        base_data = self.compute_base_predictions_new(test_set, used_features)
        step_elapsed = time() - step_time
        logger.info(f"Step - compute base predictions: {step_elapsed:.2f} seconds")
        
        step_time = time()
        test_set = self.merge_predictions(test_set, base_data)
        logger.info(f"merged predictions")
        #test_set = self.data_handler.bin_numeric_columns(test_set, nb_bins_numerical, self.features, self.non_excluded_features)
        logger.info(f"bin numeric columns")
        predicted_base = self.data_handler.calculate_weighted_aggregations(test_set, self.non_excluded_features, used_features)
        logger.info(f"calculate weighted aggregations")
        predicted_base_df = self.data_handler.construct_final_dataframe(predicted_base)
        logger.info(f"construct final dataframe")
        predicted_base_df['dataset'] = 'test'
        step_elapsed = time() - step_time
        logger.info(f"Step - finalize test predicted base: {step_elapsed:.2f} seconds")
        
        step_time = time()
        base_data_train = self.compute_base_predictions_new(train_set, used_features)
        train_set = self.merge_predictions(train_set, base_data)
        #train_set = self.data_handler.bin_numeric_columns(train_set, nb_bins_numerical, self.features, self.non_excluded_features)
        predicted_base_train = self.data_handler.calculate_weighted_aggregations(train_set, self.non_excluded_features, used_features)
        predicted_base_train_df = self.data_handler.construct_final_dataframe(predicted_base_train)
        predicted_base_train_df['dataset'] = 'train'
        step_elapsed = time() - step_time
        logger.info(f"Step - same same for train: {step_elapsed:.2f} seconds")
        
        self.predicted_base_df = predicted_base_df.append(predicted_base_train_df)
        return self.predicted_base_df.copy()
    
    def get_lift_chart(self, nb_bins):
        """
        Calculates and returns the lift chart data for the model on the training set,
        divided into the specified number of bins.

        Args:
            nb_bins (int): The number of bins to divide the data into for the lift chart.

        Returns:
            pd.DataFrame: The aggregated lift chart data with observed and predicted metrics.
        """
        train_set_df = self.train_set
        #train_set_df = pd.DataFrame(train_set)
        
        tempdata = self.data_handler.sort_and_cumsum_exposure(train_set_df, self.exposure)
        binned_data = self.data_handler.bin_data(tempdata, nb_bins)
        
        new_data = train_set_df.join(binned_data[['bin']], how='inner')
        lift_chart_data = self.data_handler.aggregate_metrics_by_bin(new_data, self.exposure, self.target)
        lift_chart_data.columns = ['Category', 'Value', 'observedAverage', 'fittedAverage']
        lift_chart_data['dataset'] = 'train'
        
        test_set_df = self.test_set
        #test_set_df = pd.DataFrame(test_set)
        
        tempdata_test = self.data_handler.sort_and_cumsum_exposure(test_set_df, self.exposure)
        binned_data_test = self.data_handler.bin_data(tempdata_test, nb_bins)
        
        new_data_test = test_set_df.join(binned_data_test[['bin']], how='inner')
        lift_chart_data_test = self.data_handler.aggregate_metrics_by_bin(new_data_test, self.exposure, self.target)
        lift_chart_data_test.columns = ['Category', 'Value', 'observedAverage', 'fittedAverage']
        lift_chart_data_test['dataset'] = 'test'
        
        return lift_chart_data.append(lift_chart_data_test)

    def get_variable_level_stats(self):
        predicted_base = self.predicted_base_df
        predicted = predicted_base[predicted_base['dataset'] == 'train'][['feature', 'category', 'exposure']]
        relativities = self.get_relativities_df()
        coef_table = self.predictor._clf.coef_table.reset_index()
        coef_table['se_pct'] = coef_table['se']/abs(coef_table['coef'])*100
        features = self.get_features()
        
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
