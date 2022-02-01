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
    check_ave_grouped = dict()
    check_ave_data['weight'] = 1
    for feature in test_df.columns:
        if feature != target_variable:
            if is_numeric_dtype(ave_data[feature].dtype):
                if len(ave_data[feature].unique()) > 20:
                    check_ave_data[feature] = [(x.left + x.right) / 2 for x in pd.cut(ave_data[feature], bins=20)]
    for feature in test_df.columns:
        if feature != target_variable:
            ave = check_ave_data.rename(columns={'base_' + feature: 'weighted_base'}).groupby([feature]).agg({'Exposure': 'sum',
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
    check_ave_grouped = dict()
    check_ave_data['weight'] = test_df['DriverAge']
    check_ave_data['Exposure'] = check_ave_data[target_variable] * check_ave_data['weight']
    check_ave_data['prediction'] = check_ave_data['prediction'] * check_ave_data['weight']
    for feature in test_df.columns:
        if feature != target_variable:
            if is_numeric_dtype(ave_data[feature].dtype):
                if len(ave_data[feature].unique()) > 20:
                    check_ave_data[feature] = [(x.left + x.right) / 2 for x in pd.cut(ave_data[feature], bins=20)]
    for feature in test_df.columns:
        if feature != target_variable:
            check_ave_data['base_' + feature] = check_ave_data['base_' + feature] * check_ave_data['weight']
            ave = check_ave_data.rename(columns={'base_' + feature: 'weighted_base'}).groupby([feature]).agg({'Exposure': 'sum',
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
        print(ave_grouped[feature])
        print(check_ave_grouped[feature])
        pd.testing.assert_frame_equal(ave_grouped[feature], check_ave_grouped[feature])
