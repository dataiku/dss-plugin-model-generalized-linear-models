custom_base_none = ('import numpy as np\n'
            'import pandas as pd\n'
            'class rebase_mode():\n'
            '    """This processor applies dummy vectorisation, but drops the dummy column with the mode. Only applies to categorical variables\n'
            '    """\n'
            '    def __init__(self):\n'
            '        self.mode_column = None\n'
            '    def fit(self, series):\n'
            '        # identify the mode of the column, returns as a text value\n'
            '        self.modalities = np.unique(series)\n'
            '        self.mode_column = series.mode()[0]\n'
            '        self.columns = set(self.modalities)\n'
            '        self.columns = list(self.columns)\n'
            '        self.columns.remove(self.mode_column)\n'
            '        self.column_name = series.name\n'
            '    def transform(self, series):\n'
            '        to_replace={m: self.mode_column for m in np.unique(series) if m not in self.modalities}\n'
            '        new_series = series.replace(to_replace=to_replace)\n'
            '        # obtains the dummy encoded dataframe, but drops the dummy column with the mode identified\n'
            '        df = pd.get_dummies(new_series.values)\n'
            '        if self.mode_column in df:\n'
            '            df = df.drop(self.mode_column, axis = 1)\n'
            '        for c in self.columns:\n'
            '            if c not in df.columns:\n'
            '                df[c] = 0\n'
            '        df = df[self.columns]\n'
            '        return df\n'
            'processor = rebase_mode()')


dku_dataset_selection_params = {'useMemTable': False,
               'filter': {'distinct': False, 'enabled': False},
               'partitionSelectionMethod': 'ALL',
               'latestPartitionsN': 1,
               'ordering': {'enabled': False, 'rules': []},
               'samplingMethod': 'FULL',
               'maxRecords': 100000,
               'targetRatio': 0.02,
               'ascending': True,
               'withinFirstN': -1,
               'maxReadUncompressedBytes': -1}