from backend.utils.dataiku_api import dataiku_api
from backend.utils.metas_utils import is_string_list_representation, convert_to_list
from functools import cache

from typing import Dict, Any, TypedDict, List, Optional
import dataiku
import pandas as pd
import ast


class FilterConfig(TypedDict):
    input_dataset: str
    filter_columns: List[str]
    filter_options: Dict[str, List[Any]]
    vector_db_type: str


def find_recipe(graph_data: Dict[str, Any], successor_id: str):
    """
    Finds the node of a given successor in a flow graph JSON data structure.

    :param graph_json: A JSON graph object
    :param successor: The successor for which to find the node.
    :return: The node
    """
    nodes = graph_data.get("nodes", {})

    for node_name, node in nodes.items():
        if successor_id in node.get("successors", []):
            return node

    raise KeyError(successor_id)


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


# Disable lists flattening for now, just show what has been configured
manage_lists = False


@cache
def get_knowledge_bank_name(id: Optional[str]) -> Optional[str]:
    if id is None:
        return None
    project = dataiku_api.default_project

    short_id = id
    if "." in id:
        (project_key, short_id) = id.split(".", 1)
    for kb in project.list_knowledge_banks():
        if kb.get('id') == short_id:
            return kb.get('name', id)
    return None

@cache
def get_llm_friendly_name(id: Optional[str]) -> Optional[str]:
    if id is None:
        return None
    project = dataiku_api.default_project
    for llm in project.list_llms():
        if llm.get('id') == id:
            return llm.get('friendlyName', id)
    return None



def compute_filter_options(input_dataset: str, columns: List[str]):
    dataset = dataiku.Dataset(
        project_key=dataiku_api.default_project_key, name=input_dataset
    )
    df: pd.DataFrame = dataset.get_dataframe(
        columns=columns, parse_dates=False)
    result = {}
    for column in df.columns:
        if manage_lists:
            if df[column].apply(lambda x: isinstance(x, str) and is_string_list_representation(x)).any():
                df[column] = df[column].apply(convert_to_list)

            if df[column].apply(lambda x: isinstance(x, list)).any():
                flattened_list = [
                    item for sublist in df[column].dropna().tolist() for item in sublist]
                unique_values = pd.unique(flattened_list)
            else:
                unique_values = pd.unique(df[column])
        else:
            unique_values = pd.unique(df[column])

        result[column] = list(unique_values)
    return result


def get_knowledge_dataset_and_filter_columns(knowledge_bank_id: str, with_options: bool = True):
    project = dataiku_api.default_project
    config = dataiku_api.webapp_config
    vector_db_type = None
    if not with_options and knowledge_bank_id:
        vector_db_type = project.get_knowledge_bank(
            knowledge_bank_id).as_core_knowledge_bank()._get()['vectorStoreType']

    flow = project.get_flow()
    graph = flow.get_graph()
    recipe_json = None
    try:
        recipe_json = find_recipe(graph.data, knowledge_bank_id)
    except KeyError:
        raise KeyError(knowledge_bank_id)

    dataset_name = recipe_json.get("predecessors")[0]
    recipe_name = recipe_json.get("ref")
    recipe = project.get_recipe(recipe_name)
    recipe_settings = recipe.get_settings()
    recipe_json_payload = recipe_settings.get_json_payload()
    kb_columns = []
    if "metadataColumns" in recipe_json_payload:
        metadataColumns = recipe_json_payload["metadataColumns"]
        if metadataColumns:
            for metadata in metadataColumns:
                if with_options:
                    if metadata["column"] in config.get('knowledge_sources_filters'):
                        kb_columns.append(metadata["column"])
                else:
                    kb_columns.append(metadata["column"])

    filter_options = {}
    if len(kb_columns) > 0 and with_options:
        filter_options = compute_filter_options(
            dataset_name, columns=kb_columns)

    return FilterConfig(
        input_dataset=dataset_name,
        filter_columns=kb_columns,
        filter_options=filter_options,
        vector_db_type=vector_db_type
    )


def get_current_filter_config():
    knwoledge_bank_id = dataiku_api.webapp_config.get(
        "knowledge_bank_id", None)
    if knwoledge_bank_id:
        try:
            result = get_knowledge_dataset_and_filter_columns(
                knwoledge_bank_id)
            return result
        except KeyError:
            return None
    return None
