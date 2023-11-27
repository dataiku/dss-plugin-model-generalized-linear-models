import pandas as pd
from glm_summary.graph_utils import compute_base_predictions, get_ave_grouped
from testing_utils import train_df, test_df, PredictorClassif
from pandas.api.types import is_numeric_dtype
from numpy.testing import assert_almost_equal


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
    base_preds_CarAge = pd.DataFrame(data=[0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
    ave_grouped = get_ave_grouped(ave_data, target_variable, weights, class_map)
    check_ave_grouped = {'Power': [0.3095238095238096, 0.5571428571, 2.857142857142857, 0.0],
                         'Density': [3778.3888888888887, 0.3611111111111111, 0.6111111111, 1.1111111111111112, 0.0]}
    
    for act, exp in zip(ave_grouped['Power'].mean(numeric_only=True).tolist(), check_ave_grouped['Power']):
        assert_almost_equal(act, exp, decimal=8)
    for act, exp in zip(ave_grouped['Density'].mean(numeric_only=True).tolist(), check_ave_grouped['Density']):
        assert_almost_equal(act, exp, decimal=8)