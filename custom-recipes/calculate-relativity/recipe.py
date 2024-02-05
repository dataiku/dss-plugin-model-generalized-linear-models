
import dataiku
import pandas as pd
import logging

from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role, get_recipe_config
from dku_config.dku_model_handler import ModelHandler
from dataiku.customrecipe import get_recipe_config
from dku_config import DkuConfig

logger = logging.getLogger(__name__)

dku_config = DkuConfig()

dku_config.add_param(
    name="dku_model",
    value=get_input_names_for_role('input_ML_Model')[0],
    required=True
)

dku_config.add_param(
    name="relativities_output_dataset_name",
    value=get_output_names_for_role('relativities_output')[0],
    required=True
)
# Example usage
model_handler = ModelHandler(dku_config.dku_model)

# Create DataFrame
relativities = model_handler.relativities_df

# Write recipe outputs
dku_output_dataset = dataiku.Dataset(dku_config.relativities_output_dataset_name)
dku_output_dataset.write_with_schema(relativities)
