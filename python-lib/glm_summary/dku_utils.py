import dataiku
from dataiku import pandasutils as pdu
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
from dataiku.customwebapp import get_webapp_config
import pandas as pd
from glm_summary.graph_utils import compute_base_predictions


def get_model_handler(model, version_id=None):
    params = model.get_predictor(version_id).params
    return PredictionModelInformationHandler(params.split_desc, params.core_params, params.model_folder,
                                             params.model_folder)


def get_original_model_handler():
    webapp_config = get_webapp_config()
    fmi = webapp_config.get("trainedModelFullModelId")
    if fmi is None:
        model = dataiku.Model(webapp_config["modelId"])
        version_id = webapp_config.get("versionId")
        original_model_handler = get_model_handler(model, version_id)
    else:
        original_model_handler = PredictionModelInformationHandler.from_full_model_id(fmi)
    return original_model_handler


# outputs all the data necessary to build the
# AvsE graphs.
def get_ave_data():
    model_handler = get_original_model_handler()
    predictor = model_handler.get_predictor()
    if model_handler.use_full_df():
        test_df = model_handler.get_full_df()[0]
    else:
        test_df = model_handler.get_test_df()[0]
    predicted = predictor.predict(test_df)
    class_map = None
    prediction_type = model_handler.get_prediction_type()
    if prediction_type == "BINARY_CLASSIFICATION":
        base_class = predicted.columns[1].split('_')[1]
        other_class = predicted.columns[2].split('_')[1]
        class_map = {base_class: 0, other_class: 1}
        predicted = pd.Series([class_map[prediction] for prediction in predicted['prediction']], name='prediction')
    if model_handler.use_full_df():
        train_df = model_handler.get_full_df()[0]
    else:
        train_df = model_handler.get_train_df()[0]
    base_predictions = compute_base_predictions(train_df, test_df, predictor, class_map)
    ave_data = pd.concat([test_df, predicted, base_predictions], axis=1)
    target_variable = model_handler.get_target_variable()
    weights = model_handler.get_sample_weight_variable()
    return ave_data, target_variable, weights, class_map