def extract_active_fullModelId(self, json_data):
    """
    Extracts the fullModelId of the active model version from the given JSON data.

    Args:
        json_data (list): A list of dictionaries containing model version details.

    Returns:
        str: The fullModelId of the active model version, or None if not found.
    """
    for item in json_data:
        if item.get('active'):
            return item['snippet'].get('fullModelId')
    return None