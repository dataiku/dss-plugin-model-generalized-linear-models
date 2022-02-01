import pandas as pd
from glm_summary.graph_utils import compute_base_predictions, get_ave_grouped
from testing_utils import train_df, test_df, PredictorClassif
from pandas.api.types import is_numeric_dtype


def test_base_predictions_classif():
    predictor = PredictorClassif()
    predictor.fit(train_df)
    class_map = {'True': 0, 'False': 1}
    base_predictions = compute_base_predictions(train_df, test_df, predictor, class_map)
    recomputed_base_predictions = dict()
    features = [4, 5]
    non_features = [i for i in range(len(test_df.columns)) if i not in features]
    base_values = {'CarAge': 0.0, 'DriverAge': 27.0}
    copy_test_df = test_df.copy()
    copy_test_df.iloc[:, 4] = base_values['CarAge']
    copy_test_df.iloc[:, 5] = base_values['DriverAge']
    base_preds = pd.DataFrame(data=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], columns=['prediction'])
    copy_test_df.iloc[:, 4] = test_df.iloc[:, 4]
    base_preds_CarAge = pd.DataFrame(data=[1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                                     columns=['prediction'])
    copy_test_df.iloc[:, 4] = base_values['CarAge']
    copy_test_df.iloc[:, 5] = test_df.iloc[:, 5]
    base_preds_DriverAge = pd.DataFrame(data=[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0],
                                        columns=['prediction'])
    check_base_predictions = pd.concat([base_preds for _ in non_features], axis=1)
    check_base_predictions.columns = ['base_' + test_df.columns[i] for i in non_features]
    check_base_predictions.insert(4, 'base_CarAge', base_preds_CarAge)
    check_base_predictions.insert(5, 'base_DriverAge', base_preds_DriverAge)
    pd.testing.assert_frame_equal(base_predictions, check_base_predictions)


def test_ave_grouped_classif():
    predictor = PredictorClassif()
    predictor.fit(train_df)
    class_map = {'True': 0, 'False': 1}
    base_predictions = compute_base_predictions(train_df, test_df, predictor, class_map)
    predicted = predictor.predict(test_df)
    predicted = pd.Series([class_map[prediction] for prediction in predicted['prediction']], name='prediction')
    ave_data = pd.concat([test_df, predicted, base_predictions], axis=1)
    target_variable = 'Exposure'
    weights = None
    ave_data[target_variable] = [str(x > 0.5) for x in ave_data[target_variable]]
    check_ave_data = ave_data.copy()
    ave_grouped = get_ave_grouped(ave_data, target_variable, weights, class_map)
    check_ave_grouped = dict()
    check_ave_data['weight'] = 1
    check_ave_data[target_variable] = pd.Series([class_map[target_value] for target_value in check_ave_data[target_variable]], name=target_variable)
    for feature in test_df.columns:
        if feature != target_variable:
            if is_numeric_dtype(ave_data[feature].dtype):
                if len(ave_data[feature].unique()) > 20:
                    check_ave_data[feature] = [(x.left + x.right) / 2 for x in pd.cut(ave_data[feature], bins=20)]
    for feature in test_df.columns:
        if feature != target_variable:
            ave = check_ave_data.rename(columns={'base_' + feature: 'weighted_base'}).groupby([feature]).agg(
                {'Exposure': 'sum',
                 'prediction': 'sum',
                 'weight': 'sum',
                 'weighted_base': 'sum'
                 }).reset_index()
            ave.columns = [feature, 'weighted_target', 'weighted_prediction',
                           'weight', 'weighted_base']
            ave['weighted_target'] = ave['weighted_target'] / ave['weight']
            ave['weighted_prediction'] = ave['weighted_prediction'] / ave['weight']
            ave['weighted_base'] = ave['weighted_base'] / ave['weight']
            check_ave_grouped[feature] = ave
    for feature in ave_grouped:
        pd.testing.assert_frame_equal(ave_grouped[feature], check_ave_grouped[feature])
