from patsy import dmatrix, build_design_matrices
from dku_config import DkuConfig

dku_config = DkuConfig()

# define variables
dku_config.add_param(
    name="column",
    value=params.get('column'),
    required=True
)

dku_config.add_param(
    name="knots",
    value=params.get('knots'),
    required=True
)

dku_config.add_param(
    name="degree",
    value=int(params.get('degree')),
    checks=[{
        "type": "between",
        "op": (0, 3)
    }],
    required=True
)

dku_config.add_param(
    name="min_value",
    value=params.get('min_value'),
    required=True
)

dku_config.add_param(
    name="max_value",
    value=params.get('max_value'),
    required=True
)

formula_string = f"bs(x, knots={dku_config.knots}, degree={dku_config.degree}, include_intercept=False)"
design_info = dmatrix(formula_string, {"x": [dku_config.min_value, dku_config.max_value]}).design_info

if dku_config.min_value>=dku_config.max_value:
    raise ValueError("max value must be greater than min value")
if min(dku_config.knots)<dku_config.min_value:
    raise ValueError("knots value must not lie under min value")
if max(dku_config.knots)>dku_config.max_value:
    raise ValueError("knots value must not lie above max value")


def process(row):

    try:
        float(row[dku_config.column])
    except:
        raise ValueError(f"Column must contain numeric data not {type(row[dku_config.column])}")
    if float(row[dku_config.column]) < dku_config.min_value:
        raise ValueError("min value must be lower than all the column values")
    if float(row[dku_config.column]) > dku_config.max_value:
        raise ValueError("max value must be greater than all the column values")
    transformed_x = build_design_matrices([design_info], {'x': [float(row[dku_config.column])]})[0][0]
    num_cols = len(transformed_x)
    new_cols = [dku_config.column + '_Spline_' + str(j-1) for j in range(1, num_cols)] # index 0 is intercept
    for i in range(1, num_cols): # index 0 is intercept
        row[new_cols[i-1]] = str(transformed_x[i])
    return row
