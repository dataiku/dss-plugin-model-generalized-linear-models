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