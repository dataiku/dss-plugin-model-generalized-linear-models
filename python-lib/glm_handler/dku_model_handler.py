import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from glm_handler.dku_utils import extract_active_fullModelId


class ModelHandler:
    """
    A class to handle interactions with a Dataiku model.

    Attributes:
        model_id (str): The ID of the model.
        model (dataiku.Model): The Dataiku model object.
        predictor (Predictor): The predictor object of the model.
        full_model_id (str): The full model ID of the active model version.
        model_info_handler (PredictionModelInformationHandler): Handler for model information.
    """

    def __init__(self, model_id):
        """
        Initializes the ModelHandler with a specific model ID.

        Args:
            model_id (str): The ID of the model to handle.
        """
        self.model_id = model_id
        self.model = dataiku.Model(model_id)
        

    def set_active_version():
        self.full_model_id = self.extract_active_fullModelId(self.model.list_versions())
        self.model_info_handler = PredictionModelInformationHandler.from_full_model_id(self.full_model_id)
        self.predictor = self.model_info_handler.get_predictor()
        self.target = self.model_info_handler.get_target_variable()
        self.compute_features()
        self.compute_base_values()
        self.compute_relativities()
        
    def get_model_versions(self):
        versions = self.model.list_versions()
        fmi_name = {version['snippet']['fullModelId']: version['snippet']['userMeta']['name'] for version in versions}
        return fmi_name
    
    def get_features(self):
        return [{'variable': feature, 
          'isInModel': self.features[feature]['role']=='INPUT', 
          'variableType': 'categorical' if self.features[feature]['type'] == 'CATEGORY' else 'numeric'} for feature in self.non_excluded_features]

    def compute_features(self):
        self.exposure = None
        self.features = self.model_info_handler.get_per_feature()
        modeling_params = self.model_info_handler.get_modeling_params()
        self.offset_columns = modeling_params['plugin_python_grid']['params']['offset_columns']
        self.exposure_columns = modeling_params['plugin_python_grid']['params']['exposure_columns']
        if len(self.exposure_columns) > 0:
            self.exposure = self.exposure_columns[0] # assumes there is only one
        important_columns = self.offset_columns + self.exposure_columns + [self.target]
        self.non_excluded_features = [feature for feature in self.features.keys() if feature not in important_columns]
        self.used_features = [feature for feature in self.non_excluded_features if self.features[feature]['role']=='INPUT']
        self.candidate_features = [feature for feature in self.non_excluded_features if self.features[feature]['role']=='REJECT']

    def compute_base_values(self):
        self.base_values = dict()
        self.modalities = dict()
        preprocessing = self.predictor.get_preprocessing()
        train_set = self.model_info_handler.get_train_df()[0].copy()
        for step in preprocessing.pipeline.steps:
            try:
                self.base_values[step.input_col] = step.processor.mode_column
                self.modalities[step.input_col] = step.processor.modalities
            except AttributeError:
                pass
        for feature in self.used_features:
            if feature not in self.base_values.keys():
                # feature has to be numerical unscaled
                if self.features[feature]['type'] == 'NUMERIC' and self.features[feature]['rescaling'] == 'NONE':
                    if self.exposure is not None:
                        self.base_values[feature] = (train_set[feature] * train_set[self.exposure]).sum() / train_set[self.exposure].sum()
                    else:
                        self.base_values[feature] = train_set[feature].mean()
                    self.modalities[feature] = {'min': train_set[feature].min(), 'max': train_set[feature].max()}
                else:
                    raise Exception("feature should be handled numerically without rescaling or categorically with the custom preprocessor")

    def compute_relativities(self):
        sample_train_row = self.model_info_handler.get_train_df()[0].head(1).copy()
        self.relativities = {}
        for feature in self.base_values.keys():
            sample_train_row[feature] = self.base_values[feature]
        if self.exposure is not None:
            sample_train_row[self.exposure] = 1
        baseline_prediction = self.predictor.predict(sample_train_row).iloc[0][0]
        for feature in self.base_values.keys():
            self.relativities[feature] = {self.base_values[feature]: 1.0}
            if self.features[feature]['type'] == 'CATEGORY':    
                for modality in self.modalities[feature]:
                    train_row_copy = sample_train_row.copy()
                    train_row_copy[feature] = modality
                    prediction = self.predictor.predict(train_row_copy).iloc[0][0]
                    self.relativities[feature][modality] = prediction/baseline_prediction
            else:
                train_row_copy = sample_train_row.copy()
                min_value = self.modalities[feature]['min']
                max_value = self.modalities[feature]['max']
                for value in np.linspace(min_value, max_value, 10):
                    train_row_copy[feature] = value
                    prediction = self.predictor.predict(train_row_copy).iloc[0][0]
                    self.relativities[feature][value] = prediction/baseline_prediction
        
        self.relativities['base'] = {'base': baseline_prediction}
        self.relativities_df = pd.DataFrame(columns=['feature', 'value', 'relativity'])

        for feature, values in self.relativities.items():
            for value, relativity in values.items():
                self.relativities_df = self.relativities_df.append({'feature': feature, 'value': value, 'relativity': relativity}, ignore_index=True)
        self.relativities_df = self.relativities_df.append({'feature': 'base', 'value': 'base', 'relativity': baseline_prediction}, ignore_index=True)

    def get_predicted_and_base_feature(self, feature, nb_bins_numerical=100000, class_map=None):
        test_set = self.model_info_handler.get_test_df()[0].copy()
        predicted = self.predictor.predict(test_set)
        test_set['predicted'] = predicted
        used_features = list(self.base_values.keys())

        if self.exposure is None:
            test_set['weight'] = 1
        else:
            test_set['weight'] = test_set[self.exposure]
        
        test_set['weighted_target'] = test_set[self.target] * test_set['weight']
        test_set['weighted_predicted'] = test_set['predicted'] * test_set['weight']
        
        # Compute base predictions
        base_data = dict()
        copy_test_df = test_set.copy()
        for other_feature in [col for col in used_features if col != feature]:
            copy_test_df[other_feature] = self.base_values[other_feature]
        predictions = self.predictor.predict(copy_test_df)
        if class_map is not None:  # classification
            base_data[feature] = pd.Series([class_map[prediction] for prediction in predictions['prediction']])
        else:
            base_data[feature] = predictions

        # compile predictions
        base_predictions = pd.concat([base_data[feature] for feature in base_data], axis=1)
        base_predictions.columns = ['base_' + feature]
        
        test_set = pd.concat([test_set, base_predictions], axis=1)

        test_set['base_' + feature] = test_set['base_' + feature] * test_set['weight']
        
        test_set[feature] = [(x.left + x.right) / 2 if isinstance(x, pd.Interval) else x for x in pd.cut(test_set[feature], bins=nb_bins_numerical)]
        
        predicted_base = {feature: test_set.rename(columns={'base_' + feature: 'weighted_base'}).groupby([feature]).agg(
                        {'weighted_target': 'sum',
                        'weighted_predicted': 'sum',
                        'weight': 'sum',
                        'weighted_base': 'sum'}).reset_index()}
        
        predicted_base[feature]['weighted_target'] = predicted_base[feature]['weighted_target'] / predicted_base[feature][
            'weight']
        predicted_base[feature]['weighted_predicted'] = predicted_base[feature]['weighted_predicted'] / \
                                                    predicted_base[feature]['weight']
        predicted_base[feature]['weighted_base'] = predicted_base[feature]['weighted_base'] / predicted_base[feature]['weight']

        predicted_base_df = pd.DataFrame(columns=['feature', 'category', 'target', 'predicted', 'exposure', 'base'])
        
        predicted_base_df = predicted_base[feature]
        predicted_base_df.columns = ['category', 'target', 'predicted', 'exposure', 'base']
        predicted_base_df['feature'] = feature
        self.predicted_base_df = self.predicted_base_df[self.predicted_base_df['feature']!=feature]
        self.predicted_base_df = self.predicted_base_df.append(predicted_base_df)
        
        return self.predicted_base_df
    
    def get_predicted_and_base(self, nb_bins_numerical=100000, class_map=None):
        test_set = self.model_info_handler.get_test_df()[0].copy()
        predicted = self.predictor.predict(test_set)
        test_set['predicted'] = predicted
        used_features = list(self.base_values.keys())
        
        if self.exposure is None:
            test_set['weight'] = 1
        else:
            test_set['weight'] = test_set[self.exposure]
        
        test_set['weighted_target'] = test_set[self.target] * test_set['weight']
        test_set['weighted_predicted'] = test_set['predicted'] * test_set['weight']
        
        # Compute base predictions
        base_data = dict()
        for feature in self.non_excluded_features:
            copy_test_df = test_set.copy()
            for other_feature in [col for col in used_features if col != feature]:
                copy_test_df[other_feature] = self.base_values[other_feature]
            predictions = self.predictor.predict(copy_test_df)
            if class_map is not None:  # classification
                base_data[feature] = pd.Series([class_map[prediction] for prediction in predictions['prediction']])
            else:
                base_data[feature] = predictions

        # compile predictions
        base_predictions = pd.concat([base_data[feature] for feature in base_data], axis=1)
        base_predictions.columns = ['base_' + feature for feature in self.non_excluded_features]

        test_set = pd.concat([test_set, base_predictions], axis=1)

        # Bin columns considered as numeric
        for feature in self.non_excluded_features:
            if self.features[feature]['type'] == 'NUMERIC':
                if len(test_set[feature].unique()) > nb_bins_numerical:
                    test_set[feature] = [(x.left + x.right) / 2 if isinstance(x, pd.Interval) else x for x in pd.cut(test_set[feature], bins=nb_bins_numerical)]

        for feature in self.non_excluded_features:
            test_set['base_' + feature] = test_set['base_' + feature] * test_set['weight']

        predicted_base = {feature: test_set.rename(columns={'base_' + feature: 'weighted_base'}).groupby([feature]).agg(
                        {'weighted_target': 'sum',
                        'weighted_predicted': 'sum',
                        'weight': 'sum',
                        'weighted_base': 'sum'}).reset_index()
                                for feature in self.non_excluded_features}
        
        for feature in self.non_excluded_features:
            predicted_base[feature]['weighted_target'] = predicted_base[feature]['weighted_target'] / predicted_base[feature][
                'weight']
            predicted_base[feature]['weighted_predicted'] = predicted_base[feature]['weighted_predicted'] / \
                                                        predicted_base[feature]['weight']
            predicted_base[feature]['weighted_base'] = predicted_base[feature]['weighted_base'] / predicted_base[feature]['weight']
        
        predicted_base_df = pd.DataFrame(columns=['feature', 'category', 'target', 'predicted', 'exposure', 'base'])

        for feature, df in predicted_base.items():
            df.columns = ['category', 'target', 'predicted', 'exposure', 'base']
            df['feature'] = feature
            predicted_base_df = predicted_base_df.append(df)
        
        self.predicted_base_df = predicted_base_df
        
        return predicted_base_df


    def get_coefficients(self):
        """
        Retrieves the coefficients of the model predictor.

        Returns:
            dict: A dictionary mapping variable names to their coefficients.
        """
        coefficients = self.predictor._model.clf.coef_
        variable_names = self.predictor._model.clf.column_labels
        return dict(zip(variable_names, coefficients))

    def get_model_predictions_on_train(self):
        """
        Generates model predictions on the training dataset.

        Returns:
            pd.DataFrame: A DataFrame of the training dataset with an additional column for predictions.
        """
        train_set = self.model_info_handler.get_train_df()[0].copy()
        predicted = self.predictor.predict(train_set)
        train_set['prediction'] = predicted
        
        return train_set['prediction']
    
    def sort_and_cumsum_exposure(self, data):
        """
        Sorts the data by prediction values in ascending order and calculates
        the cumulative sum of exposure, normalized by the total exposure.

        Args:
            data (pd.DataFrame): The DataFrame containing model predictions and exposures.

        Returns:
            pd.DataFrame: The input DataFrame with additional columns for the cumulative sum
                          and binning information based on exposure.
        """
        tempdata = data.sort_values(by='prediction', ascending=True)
        tempdata['exposure_cumsum'] = tempdata[self.exposure].cumsum() / tempdata[self.exposure].sum()
        return tempdata


    def bin_data(self, data, nb_bins):
        """
        Bins the data into specified number of bins based on the cumulative sum of exposure.

        Args:
            data (pd.DataFrame): The DataFrame containing cumulative sum of exposures.
            nb_bins (int): The number of bins to divide the data into.

        Returns:
            pd.DataFrame: The input DataFrame with a new column indicating the bin for each row.
        """
        bins = [round(x / nb_bins, 8) for x in range(nb_bins + 1)][:-1] + [float("inf")]
        data['bin'] = pd.cut(data['exposure_cumsum'].round(16), bins=bins, labels=[x + 1 for x in range(nb_bins)])
        data['bin'] = data['bin'].astype(int)
        return data
    
    def aggregate_metrics_by_bin(self, data):
        """
        Aggregates and calculates metrics within each bin, including sum of exposures,
        weighted predictions, and targets, and calculates observed and predicted data metrics.

        Args:
            data (pd.DataFrame): The DataFrame with predictions, targets, and bin information.

        Returns:
            pd.DataFrame: A summarized DataFrame with metrics calculated for each bin.
        """
        data['weighted_prediction'] = data.prediction * data[self.exposure]
        data['weighted_target'] = data[self.target] * data[self.exposure]
        grouped = data.groupby(["bin"]).aggregate({
            self.exposure: 'sum',
            'weighted_target': 'sum',
            'weighted_prediction': 'sum'
        })
        grouped['observedData'] = grouped['weighted_target'] / grouped[self.exposure]
        grouped['predictedData'] = grouped['weighted_prediction'] / grouped[self.exposure]
        grouped.reset_index(inplace=True)
        grouped.drop(['weighted_target', 'weighted_prediction'], axis=1, inplace=True)
        return grouped


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
        
        tempdata = self.sort_and_cumsum_exposure(train_set)
        binned_data = self.bin_data(tempdata, nb_bins)
        
        new_data = train_set.join(binned_data[['bin']], how='inner')
        lift_chart_data = self.aggregate_metrics_by_bin(new_data)
        return lift_chart_data


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

    def preprocess_dataframe(self, df):
        """
        Preprocesses a DataFrame using the model's preprocessing steps.

        Args:
            df (pd.DataFrame): The DataFrame to preprocess.

        Returns:
            pd.DataFrame: The preprocessed DataFrame.
        """
        column_names = self.predictor.get_features()
        preprocessed_values = self.predictor.preprocess(df)[0]
        return pd.DataFrame(preprocessed_values, columns=column_names)

