
import dataiku
from dataiku.customrecipe import *
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from commons import *

from regression_splines.dku_reg_splines import RegressionSplines

# define inputs
(input_dataset, output_dataset) = get_input_output()
recipe_config = get_recipe_config()

column_name = recipe_config.get('column_name')
knots = recipe_config.get('knots')
degree_freedom = recipe_config.get('degree_freedom')
new_col_prefix = recipe_config.get('new_col_prefix')


df = input_dataset.get_dataframe()


RegSpines = RegressionSplines(column_name, degree_freedom, knots,new_col_prefix)
output_dataset_df = RegSpines.run_spline_creation(df,keep_original=True)

# Write recipe outputs
output_dataset.write_with_schema(output_dataset_df)
