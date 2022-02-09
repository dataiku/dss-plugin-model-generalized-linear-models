import pandas as pd
from glm_summary.graph_utils import compute_base_predictions, get_ave_grouped
from testing_utils import train_df, test_df, Predictor
from pandas.api.types import is_numeric_dtype


def test_base_predictions():
    predictor = Predictor()
    predictor.fit(train_df)
    base_predictions = compute_base_predictions(train_df, test_df, predictor)
    recomputed_base_predictions = dict()
    features = [4, 5]
    non_features = [i for i in range(len(test_df.columns)) if i not in features]
    base_values = {'CarAge': 0.0, 'DriverAge': 27.0}
    copy_test_df = test_df.copy()
    copy_test_df.iloc[:, 4] = base_values['CarAge']
    copy_test_df.iloc[:, 5] = base_values['DriverAge']
    base_preds = pd.DataFrame(data=[0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565], columns=['prediction'])
    copy_test_df.iloc[:, 4] = test_df.iloc[:, 4]
    base_preds_CarAge = pd.DataFrame(data=[0.37327435606892667, 0.37327435606892667, 0.31292426809455565, 0.5844996639792254, 0.31292426809455565, 0.31292426809455565, 0.5543246199920399, 0.43362444404329775, 0.31292426809455565, 0.46379948803048326, 0.31292426809455565, 0.31292426809455565, 0.40344940005611224, 0.40344940005611224, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.31292426809455565, 0.34309931208174116], columns=['prediction'])
    copy_test_df.iloc[:, 4] = base_values['CarAge']
    copy_test_df.iloc[:, 5] = test_df.iloc[:, 5]
    base_preds_DriverAge = pd.DataFrame(data=[0.38450545354105004, 0.38450545354105004, 0.4040275950264576, 0.2868947461140122, 0.3519685510653707, 0.4170423560167293, 0.3324464095799632, 0.39752021453132175, 0.33895379007509907, 0.46259401948268025, 0.37799807304591415, 0.4691013999778161, 0.3454611705702349, 0.3259390290848273, 0.3259390290848273, 0.46259401948268025, 0.514653063443767, 0.4040275950264576, 0.47560878047295196, 0.43656449750213683], columns=['prediction'])
    check_base_predictions = pd.concat([base_preds for _ in non_features], axis=1)
    check_base_predictions.columns = ['base_' + test_df.columns[i] for i in non_features]
    check_base_predictions.insert(4, 'base_CarAge', base_preds_CarAge)
    check_base_predictions.insert(5, 'base_DriverAge', base_preds_DriverAge)
    pd.testing.assert_frame_equal(base_predictions, check_base_predictions)


def test_ave_grouped():
    predictor = Predictor()
    predictor.fit(train_df)
    base_predictions = compute_base_predictions(train_df, test_df, predictor)
    predicted = predictor.predict(test_df)
    ave_data = pd.concat([test_df, predicted, base_predictions], axis=1)
    check_ave_data = ave_data.copy()
    target_variable = 'Exposure'
    weights = None
    class_map = None
    ave_grouped = get_ave_grouped(ave_data, target_variable, weights, class_map)
    check_ave_grouped = {'Power': [0.5476666666666666, 0.46324859921954525, 2.857142857142857, 0.31292426809455565],
                         'Density': [3778.3888888888887, 0.5413888888888888, 0.4554869298672325, 1.1111111111111112, 0.3129242680945556]}
    assert ave_grouped['Power'].mean().tolist() == check_ave_grouped['Power']
    assert ave_grouped['Density'].mean().tolist() == check_ave_grouped['Density']


def test_ave_grouped_weights():
    predictor = Predictor()
    predictor.fit(train_df)
    base_predictions = compute_base_predictions(train_df, test_df, predictor)
    predicted = predictor.predict(test_df)
    ave_data = pd.concat([test_df, predicted, base_predictions], axis=1)
    check_ave_data = ave_data.copy()
    target_variable = 'Exposure'
    weights = 'DriverAge'
    class_map = None
    ave_grouped = get_ave_grouped(ave_data, target_variable, weights, class_map)
    check_ave_grouped = {'Power': [0.5634978725897064, 0.4650000101091965, 113.14285714285714, 0.31292426809455565],
                         'Density': [3778.3888888888887, 0.5413888888888888, 0.4554869298672325, 44.0,
                                     0.3129242680945556]}
    assert ave_grouped['Power'].mean().tolist() == check_ave_grouped['Power']
    assert ave_grouped['Density'].mean().tolist() == check_ave_grouped['Density']
