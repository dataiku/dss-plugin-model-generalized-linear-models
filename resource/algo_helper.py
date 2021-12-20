def get_offset_mode(config):
    choices = [{
        "value": "BASIC",
        "label": "Basic"
    },
    {
        "value": "OFFSET",
        "label": "Offset"
    }]
    distributions = ['binomial', 'gamma', 'gaussian', 'inverse_gaussian', 'poisson', 'negative_binomial', 'tweedie']
    conditions = [(config['family_name'] == distribution and config[distribution + '_link'] == 'log') for distribution in distributions]
    if any(conditions):
        choices.append({"value": "EXPOSURE",
                        "label": "Exposure"})
    return choices


def do(payload, config, plugin_config, inputs):
    if payload.get('parameterName') == 'offset_mode':
        choices = get_offset_mode(config)
    return {"choices": choices}