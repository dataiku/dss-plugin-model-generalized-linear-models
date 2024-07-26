import re
from flask import current_app
from logging_assist.logging import logger
from model_cache.model_conformity_checker import ModelConformityChecker
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