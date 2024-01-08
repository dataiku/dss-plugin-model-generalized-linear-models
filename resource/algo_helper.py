def get_offset_mode(config):
    choices = [{
        "value": "BASIC",
        "label": "Basic"
    },
    {
        "value": "OFFSETS",
        "label": "Offsets"
    }]
    link_is_log = (config[config["family_name"]+ '_link'] == 'log')

    if link_is_log:
        choices.append({"value": "OFFSETS/EXPOSURES",
                        "label": "Offsets/Exposures"})
    return choices


def do(payload, config):
    if payload.get('parameterName') == 'offset_mode':
        choices = get_offset_mode(config)
    return {"choices": choices}