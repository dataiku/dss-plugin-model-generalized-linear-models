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
    conditions = [(config['family_name']==distribution and config[distribution + '_link']=='log') for distribution in distributions]
    if any(conditions):
        choices.append({value: "EXPOSURE",
                        label: "Exposure"})
    return choices

def get_offset_column():
    choices = []
    return choices

def do(payload, config, plugin_config, inputs):
    print(payload)
    print(config)
    print(plugin_config)
    print(inputs)
    choices = [{
        "value": "BASIC",
        "label": str(payload)
    },
    {
        "value": "OFFSET",
        "label": str(config)
    },
    {
        "value": "EXPOSURE",
        "label": str(plugin_config)
    },
    {
        "value": "EXPOSURE111",
        "label": str(inputs)
    }]
    return {"choices": choices}
    if payload.get('parameterName') == 'offset_mode':
        choices = get_offset_mode(config)
    #elif payload.get('parameterName') == 'offset_column':
    #    choices = get_offset_column()
    return {"choices": choices}