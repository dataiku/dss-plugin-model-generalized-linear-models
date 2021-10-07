import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from patsy import dmatrix


class RegressionSplines:
    """
    Class for fitting Regression splines (from prepare recipes)
    """
    def __init__(self, column_name, degree_freedom, knots, new_col_prefix):
        self.column_name = column_name
        self.degree_freedom = degree_freedom
        self.knots = knots
        self.new_col_prefix = new_col_prefix
        if not isinstance(self.degree_freedom, int):
            raise TypeError('degree_freedom must be int')
        if not isinstance(self.knots, list):
            raise TypeError('knots must be a list')
        for knot in self.knots:
            if not isinstance(knot, (float, int)):
                raise TypeError('each knot must be numeric')
        self.formula_string = f"bs(train, knots={self.knots}, degree={self.degree_freedom}, include_intercept=False)"

    def rename_columns(self, df):
        """
        rename columns using the prefix provided by the user
        """
        num_cols = len(df.columns)
        new_cols = [new_col_prefix + '_' + str(j) for j in range(num_cols)]
        df.columns = new_cols

    def concatenate(self, original_df, feature_splines, keep_original=True):
        """
        combines the new regression spline columns with the original dataframe
        """
        if not keep_original:
            original_df = original_df.drop(self.column_name)

        return pd.concat([original_df, feature_splines], axis=1)

    def generate_splines(self, df):
        """
        creates regression splines df using column input provided by user
        """
        train_x = df[self.column_name]
        transformed_x = dmatrix(self.formula_string, {"train": train_x}, return_type='dataframe')
        transformed_x.drop('Intercept', axis=1, inplace=True)
        return transformed_x

    def run_spline_creation(self, df, keep_original):
        """
        main func for running
        """
        feature_splines = self.generate_splines(df)
        self.rename_columns(feature_splines)

        new_df = self.concatenate(df, feature_splines, keep_original)

        return new_df
