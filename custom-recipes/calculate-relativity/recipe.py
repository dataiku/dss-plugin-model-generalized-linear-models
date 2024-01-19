
import dataiku
import pandas as pd

from dataiku.customrecipe import get_input_names_for_role
from dataiku.customrecipe import get_output_names_for_role
from dataiku.customrecipe import get_recipe_config
from relativity_calculations.relativity_calculator import RelativityCalculator
from relativity_calculations.base_calculations import calculate_base_values
from dku_config.dku_model_handler import ModelHandler
import logging
from dataiku.customrecipe import get_recipe_config

logger = logging.getLogger(__name__)

recipe_config = get_recipe_config()

logger.info(f"Recipe Config is{recipe_config}")
logger.info(f"Inpouts are {get_input_names_for_role('input_ML_Model')}")

dku_model = get_input_names_for_role('input_ML_Model')[0]

# Example usage
model_handler = ModelHandler(dku_model)
coefficients = model_handler.get_coefficients()
preprocessed_df = model_handler.preprocess_dataframe(model_handler.get_dataframe('train'))
base_values = calculate_base_values(preprocessed_df)
relativity_calculator = RelativityCalculator(coefficients, base_values)
relativities = relativity_calculator.calculate_relativities()

variable_names = list(coefficients.keys())
# Merge dictionaries
combined_data = {var: {'Coefficient': coefficients[var], 
                       'Base Value': base_values[var], 
                       'Relativity': relativities[var]} for var in variable_names}

# Create DataFrame
df = pd.DataFrame.from_dict(combined_data, orient='index')


output_dataset_name = get_output_names_for_role('output_dataset')[0]
# Write recipe outputs
nothing = dataiku.Dataset(output_dataset_name)
nothing.write_with_schema(df)
