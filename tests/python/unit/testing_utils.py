import pandas as pd
from io import StringIO
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

testing_dict = {
    'test1': {
        'family_name': 'binomial',
        'binomial_link': 'log',
        'gamma_link': None,
        'gaussian_link': None,
        'inverse_gaussian_link': None,
        'poisson_link': None,
        'negative_binomial_link': None,
        'tweedie_link': None
    },
    'test2': {
        'family_name': 'gamma',
        'binomial_link': None,
        'gamma_link': 'identity',
        'gaussian_link': None,
        'inverse_gaussian_link': None,
        'poisson_link': None,
        'negative_binomial_link': None,
        'tweedie_link': None
    },
    'test3': {
        'family_name': 'gaussian',
        'binomial_link': None,
        'gamma_link': None,
        'gaussian_link': 'inverse_power',
        'inverse_gaussian_link': None,
        'poisson_link': None,
        'negative_binomial_link': None,
        'tweedie_link': None
    },
    'test4': {
        'family_name': 'inverse_gaussian',
        'binomial_link': None,
        'gamma_link': None,
        'gaussian_link': None,
        'inverse_gaussian_link': 'inverse_squared',
        'poisson_link': None,
        'negative_binomial_link': None,
        'tweedie_link': None
    },
    'test5': {
        'family_name': 'poisson',
        'binomial_link': None,
        'gamma_link': None,
        'gaussian_link': None,
        'inverse_gaussian_link': None,
        'poisson_link': 'log',
        'negative_binomial_link': None,
        'tweedie_link': None
    },
    'test6': {
        'family_name': 'negative_binomial',
        'binomial_link': None,
        'gamma_link': None,
        'gaussian_link': None,
        'inverse_gaussian_link': None,
        'poisson_link': None,
        'negative_binomial_link': 'cloglog',
        'tweedie_link': None
    },
    'test7': {
        'family_name': 'tweedie',
        'binomial_link': None,
        'gamma_link': None,
        'gaussian_link': None,
        'inverse_gaussian_link': None,
        'poisson_link': None,
        'negative_binomial_link': None,
        'tweedie_link': 'power'
    }
}

testing_dict_errors = {
    'test1': {
        'family_name': 'binomial',
        'binomial_link': None,
        'gamma_link': 'identity',
        'gaussian_link': None,
        'inverse_gaussian_link': None,
        'poisson_link': None,
        'negative_binomial_link': None,
        'tweedie_link': None
    },
    'test2': {
        'family_name': 'nimp',
        'binomial_link': None,
        'gamma_link': None,
        'gaussian_link': None,
        'inverse_gaussian_link': None,
        'poisson_link': None,
        'negative_binomial_link': None,
        'tweedie_link': None
    },
    'test3': {
        'family_name': 'gaussian',
        'binomial_link': None,
        'gamma_link': None,
        'gaussian_link': 'wronglink',
        'inverse_gaussian_link': None,
        'poisson_link': None,
        'negative_binomial_link': None,
        'tweedie_link': None
    }
}

train_df = pd.read_csv(StringIO('ClaimNb,Exposure,ClaimFrequency,Power,CarAge,DriverAge,DriverAgeBin,Brand,Gas,'
                                'Region,Density,ClaimAmount,DriverAge_Spline_0,DriverAge_Spline_1,'
                                'DriverAge_Spline_2\n0,0,0.09,0.0,g,0.0,46.0,45 : 50,Japanese (except Nissan) or '
                                'Korean,Diesel,Aquitaine,76,0,0.5333333333333333,0.4666666666666667,0.0\n1,0,0.84,'
                                '0.0,g,0.0,46.0,45 : 50,Japanese (except Nissan) or Korean,Diesel,Aquitaine,76,0,'
                                '0.5333333333333333,0.4666666666666667,0.0\n2,0,0.15,0.0,g,0.0,41.0,40 : 45,'
                                'Japanese (except Nissan) or Korean,Diesel,Pays-de-la-Loire,60,0,0.6444444444444445,'
                                '0.35555555555555557,0.0\n3,0,0.81,0.0,d,1.0,27.0,25 : 30,Japanese (except Nissan) or '
                                'Korean,Regular,Aquitaine,695,0,0.9555555555555556,0.044444444444444446,0.0\n4,0,'
                                '0.05,0.0,d,0.0,27.0,25 : 30,Japanese (except Nissan) or Korean,Regular,Aquitaine,'
                                '695,0,0.9555555555555556,0.044444444444444446,0.0\n5,0,0.34,0.0,i,0.0,44.0,40 : 45,'
                                'Japanese (except Nissan) or Korean,Regular,Ile-de-France,27000,0,0.5777777777777778,'
                                '0.4222222222222222,0.0\n6,0,0.1,0.0,f,2.0,32.0,30 : 35,Japanese (except Nissan) or '
                                'Korean,Diesel,Centre,23,0,0.8444444444444444,0.15555555555555556,0.0\n7,0,0.77,0.0,'
                                'f,2.0,32.0,30 : 35,Japanese (except Nissan) or Korean,Diesel,Centre,23,0,'
                                '0.8444444444444444,0.15555555555555556,0.0\n8,0,0.55,0.0,e,0.0,33.0,30 : 35,'
                                'Japanese (except Nissan) or Korean,Regular,Ile-de-France,1746,0,0.8222222222222223,'
                                '0.17777777777777778,0.0\n9,0,0.19,0.0,e,0.0,33.0,30 : 35,Japanese (except Nissan) or '
                                'Korean,Regular,Ile-de-France,1746,0,0.8222222222222223,0.17777777777777778,0.0\n10,'
                                '0,0.87,0.0,e,0.0,54.0,50 : 55,Japanese (except Nissan) or Korean,Regular,'
                                'Nord-Pas-de-Calais,781,0,0.35555555555555557,0.6444444444444445,0.0\n11,0,0.8,0.0,e,'
                                '0.0,69.0,65 : 70,Japanese (except Nissan) or Korean,Regular,Ile-de-France,1376,0,'
                                '0.022222222222222223,0.9777777777777779,0.0\n12,0,0.07,0.0,e,0.0,69.0,65 : 70,'
                                'Japanese (except Nissan) or Korean,Regular,Ile-de-France,1376,0,'
                                '0.022222222222222223,0.9777777777777779,0.0\n13,0,0.12,0.0,i,0.0,43.0,40 : 45,'
                                'Japanese (except Nissan) or Korean,Regular,Ile-de-France,7752,0,0.6,0.4,0.0\n14,0,'
                                '0.81,0.0,h,0.0,50.0,50 : 55,Japanese (except Nissan) or Korean,Regular,'
                                'Ile-de-France,3545,0,0.4444444444444445,0.5555555555555556,0.0\n15,0,0.05,0.0,h,0.0,'
                                '50.0,50 : 55,Japanese (except Nissan) or Korean,Regular,Ile-de-France,3545,0,'
                                '0.4444444444444445,0.5555555555555556,0.0\n16,0,0.71,0.0,j,8.0,30.0,30 : 35,'
                                'Japanese (except Nissan) or Korean,Regular,Ile-de-France,3661,0,0.888888888888889,'
                                '0.11111111111111112,0.0\n17,0,0.87,0.0,e,0.0,73.0,70 : 75,Japanese (except Nissan) '
                                'or Korean,Regular,Nord-Pas-de-Calais,174,0,0.0,0.896551724137931,'
                                '0.10344827586206896\n18,0,0.1,0.0,i,4.0,40.0,40 : 45,Japanese (except Nissan) or '
                                'Korean,Regular,Ile-de-France,3366,0,0.6666666666666667,0.33333333333333337,0.0\n19,'
                                '0,0.72,0.0,e,0.0,45.0,45 : 50,Japanese (except Nissan) or Korean,Regular,'
                                'Poitou-Charentes,965,0,0.5555555555555556,0.4444444444444445,0.0\n'))
test_df = pd.read_csv(StringIO('ClaimNb,Exposure,ClaimFrequency,Power,CarAge,DriverAge,DriverAgeBin,Brand,Gas,Region,Density,'
             'ClaimAmount,DriverAge_Spline_0,DriverAge_Spline_1,DriverAge_Spline_2\n0,0,0.52,0.0,f,2.0,38.0,'
             '35 : 40,Japanese (except Nissan) or Korean,Regular,Nord-Pas-de-Calais,3003,0,'
             '0.7111111111111111,0.2888888888888889,0.0\n1,0,0.45,0.0,f,2.0,38.0,35 : 40,Japanese (except '
             'Nissan) or Korean,Regular,Nord-Pas-de-Calais,3003,0,0.7111111111111111,0.2888888888888889,'
             '0.0\n2,0,0.75,0.0,g,0.0,41.0,40 : 45,Japanese (except Nissan) or Korean,Diesel,'
             'Pays-de-la-Loire,60,0,0.6444444444444445,0.35555555555555557,0.0\n3,0,0.76,0.0,d,9.0,23.0,'
             '20 : 25,Fiat,Regular,Nord-Pas-de-Calais,7887,0,0.7142857142857142,0.0,0.0\n4,0,0.01,0.0,e,0.0,'
             '33.0,30 : 35,Japanese (except Nissan) or Korean,Regular,Ile-de-France,1746,0,'
             '0.8222222222222223,0.17777777777777778,0.0\n5,0,0.76,0.0,i,0.0,43.0,40 : 45,Japanese (except '
             'Nissan) or Korean,Regular,Ile-de-France,7752,0,0.6,0.4,0.0\n6,0,0.16,0.0,j,8.0,30.0,30 : 35,'
             'Japanese (except Nissan) or Korean,Regular,Ile-de-France,3661,0,0.888888888888889,'
             '0.11111111111111112,0.0\n7,0,0.84,0.0,i,4.0,40.0,40 : 45,Japanese (except Nissan) or Korean,'
             'Regular,Ile-de-France,3366,0,0.6666666666666667,0.33333333333333337,0.0\n8,0,0.87,0.0,j,0.0,'
             '31.0,30 : 35,Japanese (except Nissan) or Korean,Diesel,Ile-de-France,27000,0,'
             '0.8666666666666667,0.13333333333333333,0.0\n9,0,0.55,0.0,l,5.0,50.0,50 : 55,Japanese (except '
             'Nissan) or Korean,Diesel,Basse-Normandie,56,0,0.4444444444444445,0.5555555555555556,0.0\n10,0,'
             '0.85,0.0,d,0.0,37.0,35 : 40,Japanese (except Nissan) or Korean,Regular,Aquitaine,175,0,'
             '0.7333333333333334,0.26666666666666666,0.0\n11,0,0.85,0.0,e,0.0,51.0,50 : 55,Japanese (except '
             'Nissan) or Korean,Regular,Nord-Pas-de-Calais,102,0,0.4222222222222222,0.5777777777777778,'
             '0.0\n12,0,0.11,0.0,d,3.0,32.0,30 : 35,"Renault, Nissan or Citroen",Regular,Nord-Pas-de-Calais,'
             '202,0,0.8444444444444444,0.15555555555555556,0.0\n13,0,0.07,0.0,e,3.0,29.0,25 : 30,"Opel, '
             'General Motors or Ford",Diesel,Pays-de-la-Loire,63,0,0.9111111111111111,0.08888888888888889,'
             '0.0\n14,0,0.09,0.0,f,0.0,29.0,25 : 30,Japanese (except Nissan) or Korean,Regular,'
             'Pays-de-la-Loire,63,0,0.9111111111111111,0.08888888888888889,0.0\n15,0,0.24,0.0,f,0.0,50.0,'
             '50 : 55,Japanese (except Nissan) or Korean,Regular,Ile-de-France,8880,0,0.4444444444444445,'
             '0.5555555555555556,0.0\n16,0,0.07,0.0,f,0.0,58.0,55 : 60,Japanese (except Nissan) or Korean,'
             'Diesel,Poitou-Charentes,23,0,0.26666666666666666,0.7333333333333334,0.0\n17,0,0.85,0.0,d,0.0,'
             '41.0,40 : 45,Japanese (except Nissan) or Korean,Regular,Ile-de-France,1784,0,'
             '0.6444444444444445,0.35555555555555557,0.0\n18,0,0.87,0.0,d,0.0,52.0,50 : 55,Japanese (except '
             'Nissan) or Korean,Regular,Centre,73,0,0.4,0.6,0.0\n19,0,0.64,0.0,i,1.0,46.0,45 : 50,'
             'Japanese (except Nissan) or Korean,Regular,Ile-de-France,2178,0,0.5333333333333333,'
             '0.4666666666666667,0.0\n'))


class Predictor:
    def __init__(self):
        self.model = LinearRegression()

    def process(self, df):
        X = df.iloc[:, [4, 5]]
        y = df.iloc[:, 1]
        return X, y

    def fit(self, df):
        X, y = self.process(df)
        self.model.fit(X, y)

    def predict(self, df):
        X, _ = self.process(df)
        return pd.DataFrame({'prediction': self.model.predict(X)})
