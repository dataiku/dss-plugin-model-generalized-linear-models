import dataiku
from dataiku import pandasutils as pdu
import pandas as pd
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
from dataiku.customwebapp import get_webapp_config

def get_model_handler(model, version_id=None):
    params = model.get_predictor(version_id).params
    return PredictionModelInformationHandler(params.split_desc, params.core_params, params.model_folder, params.model_folder)

def get_original_model_handler():
    fmi = get_webapp_config().get("trainedModelFullModelId")
    print(fmi)
    if fmi is None:
        model = dataiku.Model(get_webapp_config()["modelId"])
        version_id = get_webapp_config().get("versionId")
        original_model_handler = get_model_handler(model, version_id)
        name = model.get_name()
    else:
        original_model_handler = PredictionModelInformationHandler.from_full_model_id(fmi)
    return original_model_handler

def get_ave_data():
    model_handler = get_original_model_handler()
    print(model_handler)
    predictor = model_handler.get_predictor()
    test_df = model_handler.get_test_df()[0]
    predicted = predictor.predict(test_df)
    ave_data = pd.concat([test_df, predicted], axis=1)
    target_variable = model_handler.get_target_variable()
    weights = model_handler.get_sample_weight_variable()
    return ave_data, target_variable, weights