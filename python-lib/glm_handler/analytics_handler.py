from dku_utils import extract_active_fullModelId
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import dataiku

class ModelHandler:
    def __init__(self, model_id):
        self.model_id = model_id
        self.model = dataiku.Model(model_id)
        self.predictor = self.model.get_predictor()
        self.full_model_id = extract_active_fullModelId(self.model.list_versions())
        self.model_info_handler = PredictionModelInformationHandler.from_full_model_id(self.full_model_id)
        
        # Initialize components
        self.metadata_handler = ModelMetadataHandler(self.model_info_handler)
        self.prediction_handler = PredictionHandler(self.predictor, self.model_info_handler)
        self.exposure = self.metadata_handler.exposure_columns[0] if self.metadata_handler.exposure_columns else None
        self.analysis_handler = AnalysisHandler(self.predictor, self.model_info_handler, self.exposure)



class ModelMetadataHandler:
    def __init__(self, model_info_handler):
        self.model_info_handler = model_info_handler
        self.features = self.model_info_handler.get_per_feature()
        self.modeling_params = self.model_info_handler.get_modeling_params()
        self.exposure_columns = self.modeling_params['plugin_python_grid']['params']['exposure_columns']
        self.offset_columns = self.modeling_params['plugin_python_grid']['params']['offset_columns']
        self.important_columns = self.offset_columns + self.exposure_columns + [self.model_info_handler.get_target_variable()]
        self.non_excluded_features = [feature for feature in self.features.keys() if feature not in self.important_columns]
        self.used_features = [feature for feature in self.non_excluded_features if self.features[feature]['role'] == 'INPUT']
        self.candidate_features = [feature for feature in self.non_excluded_features if self.features[feature]['role'] == 'REJECT']

    def get_model_versions(self):
        versions = self.model.list_versions()
        return {version['snippet']['fullModelId']: version['snippet']['userMeta']['name'] for version in versions}

    def get_features(self):
        return [{'variable': feature,
                 'isInModel': self.features[feature]['role'] == 'INPUT',
                 'variableType': 'categorical' if self.features[feature]['type'] == 'CATEGORY' else 'numeric'}
                for feature in self.non_excluded_features]

    
import pandas as pd

class PredictionHandler:
    def __init__(self, predictor, model_info_handler):
        self.predictor = predictor
        self.model_info_handler = model_info_handler

    def preprocess_dataframe(self, df):
        column_names = self.predictor.get_features()
        preprocessed_values = self.predictor.preprocess(df)[0]
        return pd.DataFrame(preprocessed_values, columns=column_names)

    def get_model_predictions_on_train(self):
        train_set = self.model_info_handler.get_train_df()[0].copy()
        predicted = self.predictor.predict(train_set)
        train_set['prediction'] = predicted
        return train_set

    def compute_base_values_and_relativities(self):
        preprocessing = self.predictor.get_preprocessing()
        train_set = self.model_info_handler.get_train_df()[0].copy()
        base_values = {}
        modalities = {}
        relativities = {}

        for feature in self.model_info_handler.get_per_feature().keys():
            if feature in self.used_features:
                try:
                    base_values[feature] = preprocessing.pipeline[feature].processor.mode_column
                    modalities[feature] = preprocessing.pipeline[feature].processor.modalities
                except AttributeError:
                    base_values[feature] = train_set[feature].mean()
                    modalities[feature] = {'min': train_set[feature].min(), 'max': train_set[feature].max()}
                
                sample_train_row = train_set.head(1).copy()
                sample_train_row[feature] = base_values[feature]
                baseline_prediction = self.predictor.predict(sample_train_row).iloc[0][0]

                for modality in modalities.get(feature, []):
                    train_row_copy = sample_train_row.copy()
                    train_row_copy[feature] = modality
                    prediction = self.predictor.predict(train_row_copy).iloc[0][0]
                    relativities[feature] = prediction / baseline_prediction

        return base_values, modalities, relativities

class AnalysisHandler:
    def __init__(self, predictor, model_info_handler, exposure):
        self.predictor = predictor
        self.model_info_handler = model_info_handler
        self.exposure = exposure

    def sort_and_cumsum_exposure(self, data):
        data_sorted = data.sort_values(by='prediction', ascending=True)
        data_sorted['exposure_cumsum'] = data_sorted[self.exposure].cumsum() / data_sorted[self.exposure].sum()
        return data_sorted

    def bin_data(self, data, nb_bins):
        bins = [round(x / nb_bins, 8) for x in range(nb_bins + 1)][:-1] + [float("inf")]
        data['bin'] = pd.cut(data['exposure_cumsum'].round(16), bins=bins, labels=[x + 1 for x in range(nb_bins)])
        data['bin'] = data['bin'].astype(int)
        return data

    def aggregate_metrics_by_bin(self, data):
        data['weighted_prediction'] = data['prediction'] * data[self.exposure]
        data['weighted_target'] = data['target'] * data[self.exposure]
        grouped = data.groupby(['bin']).aggregate({
            self.exposure: 'sum',
            'weighted_target': 'sum',
            'weighted_prediction': 'sum'
        }).reset_index()
        grouped['observedData'] = grouped['weighted_target'] / grouped[self.exposure]
        grouped['predictedData'] = grouped['weighted_prediction'] / grouped[self.exposure]
        return grouped

    def get_lift_chart(self, nb_bins):
        train_set = self.get_model_predictions_on_train()
        tempdata = self.sort_and_cumsum_exposure(train_set)
        binned_data = self.bin_data(tempdata, nb_bins)
        lift_chart_data = self.aggregate_metrics_by_bin(binned_data)
        return lift_chart_data