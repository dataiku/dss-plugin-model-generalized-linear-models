
import dataiku
import pandas as pd
import logging

from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role, get_recipe_config
from relativity_calculations.relativity_calculator import RelativityCalculator
from relativity_calculations.base_calculations import calculate_base_values
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
coefficients = model_handler.get_coefficients()
link_function = model_handler.get_link_function()
preprocessed_df = model_handler.preprocess_dataframe(model_handler.get_dataframe('train'))
base_values = calculate_base_values(preprocessed_df)

relativity_calculator = RelativityCalculator(coefficients, base_values, link_function)
relativities = relativity_calculator.calculate_relativities()

variable_names = list(coefficients.keys())

# Merge dictionaries
combined_data = {var: {'Coefficient': coefficients[var], 
                       'Base Value': base_values[var], 
                       'Relativity': relativities[var]} for var in variable_names}

# Create DataFrame
df = pd.DataFrame.from_dict(combined_data, orient='index')


# Write recipe outputs
dku_output_dataset = dataiku.Dataset(dku_config.relativities_output_dataset_name)
dku_output_dataset.write_with_schema(df.reset_index())
