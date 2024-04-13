import dataiku
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
import pandas as pd
import numpy as np
from dataiku import pandasutils as pdu
from glm_handler.dku_utils import extract_active_fullModelId

from backend.logging_settings import logger


class GlmDataHandler():
    def __init__(self):
        pass
    
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

    def sort_and_cumsum_exposure(self, data, exposure):
        """
        Sorts the data by prediction values in ascending order and calculates
        the cumulative sum of exposure, normalized by the total exposure.

        Args:
            data (pd.DataFrame): The DataFrame containing model predictions and exposures.

        Returns:
            pd.DataFrame: The input DataFrame with additional columns for the cumulative sum
                          and binning information based on exposure.
        """
        print(f"Pandas version is {pd.__version__}")
        print(f"data is type {type(data)}")
        tempdata = data.sort_values(by='prediction', ascending=True)
        tempdata['exposure_cumsum'] = tempdata[exposure].cumsum() / tempdata[exposure].sum()
        return tempdata
    
    def aggregate_metrics_by_bin(self, data, exposure, target):
        """
        Aggregates and calculates metrics within each bin, including sum of exposures,
        weighted predictions, and targets, and calculates observed and predicted data metrics.

        Args:
            data (pd.DataFrame): The DataFrame with predictions, targets, and bin information.

        Returns:
            pd.DataFrame: A summarized DataFrame with metrics calculated for each bin.
        """
        data['weighted_prediction'] = data.prediction * data[exposure]
        data['weighted_target'] = data[target] * data[exposure]
        grouped = data.groupby(["bin"]).aggregate({
            exposure: 'sum',
            'weighted_target': 'sum',
            'weighted_prediction': 'sum'
        })
        grouped['observedData'] = grouped['weighted_target'] / grouped[exposure]
        grouped['predictedData'] = grouped['weighted_prediction'] / grouped[exposure]
        grouped.reset_index(inplace=True)
        grouped.drop(['weighted_target', 'weighted_prediction'], axis=1, inplace=True)
        return grouped
    
    def calculate_weighted_aggregations(self, test_set, non_excluded_features):
        predicted_base = {feature: test_set.rename(columns={'base_' + feature: 'weighted_base'}).groupby([feature]).agg(
            {'weighted_target': 'sum',
             'weighted_predicted': 'sum',
             'weight': 'sum',
             'weighted_base': 'sum'}).reset_index()
            for feature in non_excluded_features}
        for feature in predicted_base:
            predicted_base[feature]['weighted_target'] /= predicted_base[feature]['weight']
            predicted_base[feature]['weighted_predicted'] /= predicted_base[feature]['weight']
            predicted_base[feature]['weighted_base'] /= predicted_base[feature]['weight']
        return predicted_base
    
    def construct_final_dataframe(self, predicted_base):
        predicted_base_df = pd.DataFrame(columns=['feature', 'category', 'target', 'predicted', 'exposure', 'base'])
        for feature, df in predicted_base.items():
            df.columns = ['category', 'target', 'predicted', 'exposure', 'base']
            df['feature'] = feature
            predicted_base_df = predicted_base_df.append(df)
        return predicted_base_df
    
    
    def preprocess_dataframe(self, df, predictor):
        """
        Preprocesses a DataFrame using the model's preprocessing steps.

        Args:
            df (pd.DataFrame): The DataFrame to preprocess.

        Returns:
            pd.DataFrame: The preprocessed DataFrame.
        """
        column_names = predictor.get_features()
        preprocessed_values = predictor.preprocess(df)[0]
        return pd.DataFrame(preprocessed_values, columns=column_names)