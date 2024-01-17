
import dataiku
import json


from backend.utils.knowledge_filters import FilterConfig, get_knowledge_dataset_and_filter_columns


def get_knowledge_bank_metas_choices(config):
    knowledge_bank_id = config.get("knowledge_bank_id")
    filer_config = get_knowledge_dataset_and_filter_columns(
        knowledge_bank_id, False)

    return {
        "choices": [{"value": meta, "label": meta} for meta in filer_config['filter_columns']]
    }


def do(payload, config, plugin_config, inputs):
    parameter_name = payload["parameterName"]
    client = dataiku.api_client()
    current_project = client.get_default_project()

    if parameter_name == "llm_id":

        return {
            "choices": [
                {"value": llm.get("id"), "label": llm.get("friendlyName")} for llm in current_project.list_llms() if llm.get('type') != 'RETRIEVAL_AUGMENTED'
            ]
        }
    elif parameter_name == "knowledge_bank_id":
        return {
            "choices": [{"value": "", "label": "None"}] + [
                {"value": kb.get("id"), "label": kb.get("name")} for kb in current_project.list_knowledge_banks()
            ]
        }
    elif parameter_name == "knowledge_sources_filters":
        return get_knowledge_bank_metas_choices(config)
    elif parameter_name == "knowledge_sources_displayed_metas":
        return get_knowledge_bank_metas_choices(config)
    elif parameter_name == "knowledge_source_url":
        return get_knowledge_bank_metas_choices(config)
    elif parameter_name == "knowledge_source_title":
        return get_knowledge_bank_metas_choices(config)
    elif parameter_name == "knowledge_source_thumbnail":
        return get_knowledge_bank_metas_choices(config)

    else:
        return {
            "choices": [
                {
                    "value": "wrong",
                    "label": f"Problem getting the name of the parameter.",
                }
            ]
        }
