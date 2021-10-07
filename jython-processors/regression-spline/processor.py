from patsy import dmatrix, build_design_matrices

column = params.get('column')
degree = int(params.get('degree'))
knots = params.get('knots')
min_value = params.get('min_value')
max_value = params.get('max_value')
formula_string = f"bs(x, knots={knots}, degree={degree}, include_intercept=False)"
design_info = dmatrix(formula_string, {"x": [min_value, max_value]}).design_info

if min_value>=max_value:
    raise ValueError("max value must be greater than min value")
if min(knots)<min_value:
    raise ValueError("knots value must not lie under min value")
if max(knots)>max_value:
    raise ValueError("knots value must not lie above max value")

def process(row):
    transformed_x = build_design_matrices([design_info], {'x': [float(row[column])]})[0][0]
    transformed_x.drop("Intercept", inplace=True, axis=1)
    num_cols = len(transformed_x.columns)
    new_cols = [new_col_prefix + '_Spline_' + str(j) for j in range(num_cols)]
    for i in range(num_cols):
        row[new_cols[i]] = str(transformed_x.iloc[0, i])
    return row
