import dataiku

client = dataiku.api_client()
project = client.get_default_project()

def do(payload, config, plugin_config, inputs):
    
    anaylsis_details = project.list_analyses()
    
    choices = [
            {
                "value": item['analysisId'],
                "label": item['analysisName']
            }
            for item in anaylsis_details
        ]
    return {"choices": choices}