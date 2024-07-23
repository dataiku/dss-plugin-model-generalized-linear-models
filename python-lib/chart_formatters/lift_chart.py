


class LiftChartFormatter:
    
    def __init__(self, model_retriever, data_handler, relativites_calculator):
        self.model_retriever = model_retriever
        self.data_handler = data_handler
        self.relativities_calculator = relativites_calculator
        
    def get_lift_chart(self, nb_bins):
        """
        Calculates and returns the lift chart data for the model on the training set,
        divided into the specified number of bins.

        Args:
            nb_bins (int): The number of bins to divide the data into for the lift chart.

        Returns:
            pd.DataFrame: The aggregated lift chart data with observed and predicted metrics.
        """
        train_set_df = self.relativities_calculator.train_set
        
        tempdata = self.data_handler.sort_and_cumsum_exposure(train_set_df, self.model_retriever.exposure_columns)
        binned_data = self.data_handler.bin_data(tempdata, nb_bins)
        
        new_data = train_set_df.join(binned_data[['bin']], how='inner')
        lift_chart_data = self.data_handler.aggregate_metrics_by_bin(new_data, self.model_retriever.exposure_columns, self.model_retriever.target_column)
        lift_chart_data.columns = ['Category', 'Value', 'observedAverage', 'fittedAverage']
        lift_chart_data['dataset'] = 'train'
        
        test_set_df = self.relativities_calculator.test_set
        
        tempdata_test = self.data_handler.sort_and_cumsum_exposure(test_set_df, self.model_retriever.exposure_columns)
        binned_data_test = self.data_handler.bin_data(tempdata_test, nb_bins)
        
        new_data_test = test_set_df.join(binned_data_test[['bin']], how='inner')
        lift_chart_data_test = self.data_handler.aggregate_metrics_by_bin(new_data_test, self.model_retriever.exposure_columns, self.model_retriever.target_column)
        lift_chart_data_test.columns = ['Category', 'Value', 'observedAverage', 'fittedAverage']
        lift_chart_data_test['dataset'] = 'test'
        
        return lift_chart_data.append(lift_chart_data_test)