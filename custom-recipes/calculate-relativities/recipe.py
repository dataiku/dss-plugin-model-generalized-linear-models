
import dataiku
import pandas as pd

from dataiku.customrecipe import get_input_names_for_role
from dataiku.customrecipe import get_output_names_for_role
from dataiku.customrecipe import get_recipe_config
from relativity_calculations.relativity_calculator import RelativityCalculator
from relativity_calculations.base_calculations import calculate_base_values
from dku_config.duk_model_handler import ModelHandler

input_A_names = get_input_names_for_role('input_A_role')

output_A_names = get_output_names_for_role('main_output')
output_A_datasets = [dataiku.Dataset(name) for name in output_A_names]


# Example usage
model_handler = ModelHandler(input_A_names[0])
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



# Write recipe outputs
nothing = dataiku.Dataset("nothing")
nothing.write_with_schema(output_A_datasets[0])
