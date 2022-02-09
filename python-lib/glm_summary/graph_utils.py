import pandas as pd
from pandas.api.types import is_numeric_dtype


def compute_base_predictions(train_df, test_df, predictor, class_map=None):
    """
    base predictions are defined as the prediction when
    all the features except the feature of interest are
    at their base value (the mode of their distribution)
    """
    # categorize numeric variables
    for feature in train_df.columns:
        if is_numeric_dtype(train_df[feature].dtype):
            if len(train_df[feature].unique()) > 20:
                train_df[feature] = [(x.left + x.right) / 2 if isinstance(x, pd.Interval) else x for x in pd.cut(train_df[feature], bins=20)]

    base_params = {col: train_df[col].mode()[0] for col in train_df.columns}

    # compute base predictions
    base_data = dict()
    for feature in test_df.columns:
        copy_test_df = test_df.copy()
        for other_feature in [col for col in test_df.columns if col != feature]:
            copy_test_df[other_feature] = base_params[other_feature]
        predictions = predictor.predict(copy_test_df)
        if class_map is not None:  # classification
            base_data[feature] = pd.Series([class_map[prediction] for prediction in predictions['prediction']])
        else:
            base_data[feature] = predictions

    # compile predictions
    base_predictions = pd.concat([base_data[feature] for feature in base_data], axis=1)
    base_predictions.columns = 'base_' + test_df.columns

    return base_predictions


def get_ave_grouped(ave_data, target, weight, class_map):
    if weight is None:
        ave_data['weight'] = 1
    else:
        ave_data['weight'] = ave_data[weight]

    if class_map is not None:  # classification
        ave_data[target] = pd.Series([class_map[target_value] for target_value in ave_data[target]], name=target)

    ave_data['weighted_target'] = ave_data[target] * ave_data['weight']
    ave_data['weighted_prediction'] = ave_data['prediction'] * ave_data['weight']

    excluded_columns = [target, 'prediction', 'weight', 'weighted_target', 'weighted_prediction'] + [feature for feature
                                                                                                     in ave_data if
                                                                                                     feature[
                                                                                                     :5] == 'base_']
    feature_names = [feature for feature in ave_data.columns if feature not in excluded_columns]

    # bin numerical features
    for feature in feature_names:
        ave_data['base_' + feature] = ave_data['base_' + feature] * ave_data['weight']
        if is_numeric_dtype(ave_data[feature].dtype):
            if len(ave_data[feature].unique()) > 20:
                ave_data[feature] = [(x.left + x.right)/2 if isinstance(x, pd.Interval) else x for x in pd.cut(ave_data[feature], bins=20)]

    ave_grouped = {feature: ave_data.rename(columns={'base_' + feature: 'weighted_base'}).groupby([feature]).agg(
        {'weighted_target': 'sum',
         'weighted_prediction': 'sum',
         'weight': 'sum',
         'weighted_base': 'sum'}).reset_index()
                   for feature in feature_names}

    for feature in ave_grouped:
        ave_grouped[feature]['weighted_target'] = ave_grouped[feature]['weighted_target'] / ave_grouped[feature][
            'weight']
        ave_grouped[feature]['weighted_prediction'] = ave_grouped[feature]['weighted_prediction'] / \
                                                      ave_grouped[feature]['weight']
        ave_grouped[feature]['weighted_base'] = ave_grouped[feature]['weighted_base'] / ave_grouped[feature]['weight']

    return ave_grouped
