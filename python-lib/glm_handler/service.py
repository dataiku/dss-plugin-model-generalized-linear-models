#from backend.dataiku_api import dataiku_api
import dataiku
import os
#from dataiku.doctor.posttraining.model_information_handler import PredictionModelInformationHandler

class GLM_Handler:
    """GLM_Handler: A class to facilitate the connection to GLM"""

    def __init__(self):
        # self.project = dataiku_api.default_project
        os.environ["DKU_CURRENT_PROJECT_KEY"] = "SOL_CLAIM_MODELING"
        self.model = dataiku.Model("aHJZVrBQ")
        print(self.model)
        print(self.model.get_info())
        #full_model_id = [version['snippet']['fullModelId'] for version in self.model.list_versions() if version['active']==True][0]
        #original_model_handler = dataiku.doctor.posttraining.model_information_handler.PredictionModelInformationHandler.from_full_model_id(full_model_id)
        #print(original_model_handler)
        #self.predictor = self.model.get_predictor()
        # if self.model.use_full_df():
        #     test_df = self.model.get_full_df()[0]
        # else:
        #     test_df = self.model.get_test_df()[0]
        # predicted = self.predictor.predict(test_df)
        # print(predicted)
        print("init")

glm_handler = GLM_Handler()
