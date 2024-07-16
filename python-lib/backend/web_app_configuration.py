from dataiku.customwebapp import get_webapp_config


class WebAppConfiguration:
    
    def __init__(self):
        web_app_config = get_webapp_config()
        self.existing_analysis_id = web_app_config.get("existing_analysis_id")
        self.input_dataset = web_app_config.get("training_dataset_string")
        self.prediction_type = web_app_config.get("prediction_type")
        self.setup_type = web_app_config.get("setup_type")
        self.policy = web_app_config.get("policy")
        self.test_dataset_string = web_app_config.get("test_dataset_string")
    