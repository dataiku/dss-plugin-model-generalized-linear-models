import dataiku
from dataiku import pandasutils as pdu
import pandas as pd
from pandas.api.types import is_numeric_dtype
from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler
from dataiku.customwebapp import get_webapp_config

def get_model_handler(model, version_id=None):
    params = model.get_predictor(version_id).params
    return PredictionModelInformationHandler(params.split_desc, params.core_params, params.model_folder, params.model_folder)

def get_original_model_handler():
    fmi = get_webapp_config().get("trainedModelFullModelId")
    if fmi is None:
        model = dataiku.Model(get_webapp_config()["modelId"])
        version_id = get_webapp_config().get("versionId")
        original_model_handler = get_model_handler(model, version_id)
        name = model.get_name()
    else:
        original_model_handler = PredictionModelInformationHandler.from_full_model_id(fmi)
    return original_model_handler

# outputs all the data necessary to build the
# AvsE graphs.
def get_ave_data():
    model_handler = get_original_model_handler()
    predictor = model_handler.get_predictor()
    test_df = model_handler.get_test_df()[0]
    predicted = predictor.predict(test_df)
    base_predictions = compute_base_predictions(model_handler, predictor)
    ave_data = pd.concat([test_df, predicted, base_predictions], axis=1)
    target_variable = model_handler.get_target_variable()
    weights = model_handler.get_sample_weight_variable()
    return ave_data, target_variable, weights

# base predictions are defined as the prediction when
# all the features except the feature of interest are
# at their base value (the mode of their distribution)
def compute_base_predictions(model_handler, predictor):
    train_df = model_handler.get_train_df()[0]
    # categorize numeric variables
    for feature in train_df.columns:
        if is_numeric_dtype(train_df[feature].dtype):
            if len(train_df[feature].unique())>20:
                train_df[feature] = [(x.left + x.right)/2 for x in pd.cut(train_df[feature], bins=20)]
    
    base_params = {col: train_df[col].mode()[0] for col in train_df.columns}
    
    # compute base predictions
    test_df = model_handler.get_test_df()[0]
    
    base_data = dict()
    for feature in test_df.columns:
        copy_test_df = test_df.copy()
        for other_feature in [col for col in test_df.columns if col!=feature]:
            copy_test_df[other_feature] = base_params[other_feature]
            base_data[feature] = predictor.predict(copy_test_df)
    
    # compile predictions
    base_predictions = pd.concat([base_data[c] for c in base_data], axis=1)
    base_predictions.columns = 'base_' + test_df.columns
    
    return base_predictions

def get_ave_grouped():
    ave_data, target, weight = get_ave_data()
    
    if weight==None:
        weight = 'weight'
        ave_data[weight] = 1

    prediction = 'prediction'
    weighted_target = 'weighted_target'
    weighted_prediction = 'weighted_prediction'
    weighted_base = 'weighted_base'
    ave_data['weighted_target'] = ave_data[target] * ave_data[weight]
    ave_data['weighted_prediction'] = ave_data[prediction] * ave_data[weight]

    excluded_columns = [target, prediction, weight, weighted_target, weighted_prediction] + [c for c in ave_data if c[:5]=='base_']
    feature_names = [c for c in ave_data.columns if c not in excluded_columns]

    # bin numerical features
    for c in feature_names:
        ave_data['base_' + c] = ave_data['base_' + c] * ave_data[weight]
        if is_numeric_dtype(ave_data[c].dtype):
            if len(ave_data[c].unique())>20:
                ave_data[c] = [x.left for x in pd.cut(ave_data[c], bins=20)]

    ave_grouped = {c: ave_data.rename(columns={'base_' + c: 'weighted_base'}).groupby([c]).agg({weighted_target: 'sum', 
                                                                                      weighted_prediction: 'sum', 
                                                                                      weight: 'sum',
                                                                                      weighted_base: 'sum'}).reset_index()
                   for c in feature_names}

    for c in ave_grouped:
        ave_grouped[c][weighted_target] = ave_grouped[c][weighted_target]/ave_grouped[c][weight]
        ave_grouped[c][weighted_prediction] = ave_grouped[c][weighted_prediction]/ave_grouped[c][weight]
        ave_grouped[c][weighted_base] = ave_grouped[c][weighted_base]/ave_grouped[c][weight]
    
    return ave_grouped