
import dataiku
from dataiku.customrecipe import get_recipe_config
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from dkulib.core.dku_config.dku_config import DkuConfig

from regression_splines.dku_reg_splines import RegressionSplines
from commons import get_input_output
# define inputs
(input_dataset, output_dataset) = get_input_output()
recipe_config = get_recipe_config()


dku_config = DkuConfig(
    local_vars=dataiku.Project().get_variables()['local'],
    local_prefix="GENERALIZED_LINEAR_MODELS_PLUGIN__"
)

# define variables
dku_config.add_param(
    name="column_name",
    value=config.get("column_name"),
    required=True
)

dku_config.add_param(
    name="knots",
    value=config.get("knots"),
    required=True
)

dku_config.add_param(
    name="degree_freedom",
    value=config.get("degree_freedom"),
    checks=[{
        "type": "between",
        "op": (1, 3)
    }],
    required=True
)

dku_config.add_param(
    name="new_col_prefix",
    value=config.get("new_col_prefix"),
    required=True
)


df = input_dataset.get_dataframe()

# fits splines
RegSpines = RegressionSplines(dku_config.column_name, dku_config.degree_freedom, dku_config.knots, dku_config.new_col_prefix)
output_dataset_df = RegSpines.run_spline_creation(df, keep_original=True)

# Write recipe outputs
output_dataset.write_with_schema(output_dataset_df)
