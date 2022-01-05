import dataiku
from dataiku.customrecipe import *
import pandas as pd, numpy as np
# from dataiku import pandasutils as pdu
import sys
import re
import generalized_linear_models

sys.modules['generalized_linear_models'] = generalized_linear_models

saved_model = get_input_names_for_role('saved_model')[0]
model = dataiku.Model(saved_model)
predictor = model.get_predictor()
# For outputs, the process is the same:
model_design = get_output_names_for_role('model_design')[0]
coefficients = get_output_names_for_role('coefficients')[0]
# Read recipe inputs
# Claim Frequency
parameters = []
values = []

link_function = predictor._clf.get_link_function()
link_find = re.search('<statsmodels.genmod.families.links.(.*) object', str(link_function))
link = link_find.group(1)

family_distribution = predictor._clf.family
family_find = re.search('<statsmodels.genmod.families.family.(.*) object', str(family_distribution))
family = family_find.group(1)

parameters.append('family')
values.append(family)
parameters.append('link')
values.append(link)
parameters.append('penalty')
values.append(predictor._clf.penalty)
parameters.append('offset_mode')
values.append(predictor._clf.offset_mode)
if predictor._clf.offset_mode != 'BASIC':
    parameters.append('offsets')
    values.append(predictor._clf.offset_columns)
if predictor._clf.offset_mode == 'OFFSETS/EXPOSURES':
    parameters.append('exposures')
    values.append(predictor._clf.exposure_columns)
if family == 'NegativeBinomial':
    parameters.append('alpha')
    values.append(predictor._clf.alpha)
if link == 'Power':
    parameters.append('power')
    values.append(predictor._clf.power)
if family == 'Tweedie':
    parameters.append('var_power')
    values.append(predictor._clf.var_power)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Write recipe outputs
model_design_df = pd.DataFrame({'parameter': parameters, 'value': values})
model_design_dataset = dataiku.Dataset(model_design)
model_design_dataset.write_with_schema(model_design_df)

coefficients_df = pd.DataFrame({'name': predictor._clf.column_labels, 'coefficient': predictor._clf.coef_})
coefficients_dataset = dataiku.Dataset(coefficients)
coefficients_dataset.write_with_schema(coefficients_df)