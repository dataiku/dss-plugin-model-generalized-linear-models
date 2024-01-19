import pandas as pd 

def calculate_base_values(df):
    """
    Calculates base values for each column in a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate base values for.

    Returns:
        dict: A dictionary mapping column names to their base values.
    """
    base_values = {}
    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            base_values[column] = df[column].mean()
        else:
            base_values[column] = df[column].mode()[0]
    return base_values

