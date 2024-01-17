from backend.models.base import Source
from backend.utils.dataiku_api import dataiku_api
from backend.utils.metas_utils import is_string_list_representation, convert_to_list


def map_sources(sources):
    new_sources = []
    config = dataiku_api.webapp_config

    for source in sources:
        # Initialize default values for title, url, and thumbnail
        source_title = ""
        source_url = ""
        source_thumbnail_url = ""
              
        if config["knowledge_source_title"] in source["metadata"]:
            source_title = source["metadata"][config["knowledge_source_title"]]

        if config["knowledge_source_url"] in source["metadata"]:
            source_url = source["metadata"][config["knowledge_source_url"]]

        if config["knowledge_source_thumbnail"] in source["metadata"]:
            source_thumbnail_url = source["metadata"][config["knowledge_source_thumbnail"]]

        new_source = Source(
            excerpt= source["excerpt"],
            metadata= {"source_title": source_title,
                       "source_url": source_url,
                       "source_thumbnail_url": source_thumbnail_url,
                       "tags": []
                       }
        )

        for meta in config["knowledge_sources_displayed_metas"]:
            value = source["metadata"].get(meta, None)
            if value is not None:
                if is_string_list_representation(value):
                    value = convert_to_list(value)
                    value_type = "list"
                else:
                    value_type = "string"

                new_source["metadata"]["tags"].append({
                    "name": meta,
                    "value": value,
                    "type": value_type
                })

        new_sources.append(new_source)

    return new_sources


