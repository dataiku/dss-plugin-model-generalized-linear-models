import re
from flask import current_app
from logging_assist.logging import logger
from model_cache.model_conformity_checker import ModelConformityChecker
import pandas as pd

pattern = r'\((.*?)\)'

mcc = ModelConformityChecker()

def format_models(global_dku_mltask):
    logger.info("Formatting Models")
    list_ml_id = global_dku_mltask.get_trained_models_ids()
    models = []
    for ml_id in list_ml_id:
        model_details = global_dku_mltask.get_trained_model_details(ml_id)
        is_conform = mcc.check_model_conformity(ml_id)
        if is_conform:
            model_name = model_details.get_user_meta()['name']
            matches = re.findall(pattern, model_name)
            models.append({"id": ml_id, "name": matches[0]})
        else:
            current_app.logger.info(f"model {ml_id} is not conform")
    return models

def np_encode(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    return obj


def natural_sort_key(s):
    import re
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(s))]

def calculate_base_levels(df, exposure_column=None, max_nb_options=100):
    cols_json = []
    # Sort the columns using natural sorting
    sorted_columns = sorted(df.columns, key=natural_sort_key)
    
    for col in sorted_columns:
        if col == exposure_column:
            continue
        
        # Determine if the column contains numeric or non-numeric data
        is_numeric = pd.api.types.is_numeric_dtype(df[col])
        
        if is_numeric:
            options = sorted([str(val) for val in df[col].unique()], key=float)
            options = options[:max_nb_options]
        else:
            options = sorted([str(val) for val in df[col].unique()], key=natural_sort_key)
            options = options[:max_nb_options]
        
        if exposure_column and exposure_column in df.columns:
            # Exposure-based calculation
            weighted_counts = df.groupby(col)[exposure_column].sum()
            base_level = str(weighted_counts.idxmax())
        else:
            # Original mode-based calculation
            base_level = str(df[col].mode().iloc[0])
        
        cols_json.append({
            'column': col,
            'options': options,
            'baseLevel': base_level
        })
    
    return cols_json