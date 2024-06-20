import re
from flask import current_app

pattern = r'\((.*?)\)'

def format_models(global_dku_mltask):
    list_ml_id = global_dku_mltask.get_trained_models_ids()
    models = []
    for ml_id in list_ml_id:
        model_details = global_dku_mltask.get_trained_model_details(ml_id)
        is_conform = check_model_conformity(model_details)
        if is_conform:
            model_name = model_details.get_user_meta()['name']
            matches = re.findall(pattern, model_name)
            models.append({"id": ml_id, "name": matches[0]})
        else:
            current_app.logger.info(f"model {ml_id} is not conform")
    return models

def check_model_conformity(model_details):
    is_glm = check_is_glm(model_details)
    no_regularization = check_no_regularization(model_details)
    no_offset = check_no_offset(model_details)
    no_weighting = check_no_weighting(model_details)
    train_test_split = check_train_test_split(model_details)
    feature_handling = check_feature_handling(model_details)
    return all([is_glm, no_regularization, no_offset, no_weighting, train_test_split, feature_handling])

def check_is_glm(model_details):
    modeling = model_details.details['modeling']
    if modeling['algorithm'] != 'CUSTOM_PLUGIN':
        return False
    if modeling['plugin_python_grid']['pluginId'] != 'generalized-linear-models':
        return False
    return True

def check_no_regularization(model_details):
    penalty = model_details.details['modeling']['plugin_python_grid']['params']['penalty']
    if penalty != [0.0]:
        return False
    return True

def check_no_offset(model_details):
    offsets = model_details.details['modeling']['plugin_python_grid']['params']['offset_columns']
    if len(offsets) > 0:
        return False
    return True

def check_no_weighting(model_details):
    weight_method = model_details.details['coreParams']['weight']['weightMethod']
    if weight_method != 'NO_WEIGHTING':
        return False
    return True

def check_train_test_split(model_details):
    tt_policy = model_details.details['splitDesc']['params']['ttPolicy']
    if (tt_policy != 'SPLIT_SINGLE_DATASET') and (tt_policy != 'EXPLICIT_FILTERING_TWO_DATASETS'):
        return False
    return True

def check_feature_handling(model_details):
    feature_handlings = model_details.details['preprocessing']['per_feature']
    for feature in feature_handlings.keys():
        feature_handling = feature_handlings[feature]
        if feature_handling['role'] == 'INPUT':
            if feature_handling['type'] == 'CATEGORY':
                if feature_handling['category_handling'] != 'CUSTOM':
                    return False
            elif feature_handling['type'] == 'NUMERIC':
                if feature_handling['rescaling'] != 'NONE':
                    return False
    return True