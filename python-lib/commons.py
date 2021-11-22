import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role
from dkulib.core.dku_config.dku_config import DkuConfig


def get_input_output():
    if len(get_input_names_for_role('input_dataset')) == 0:
        raise ValueError('No input dataset.')
    if len(get_output_names_for_role('output_dataset')) == 0:
        raise ValueError('No output dataset.')
    input_dataset_name = get_input_names_for_role('input_dataset')[0]
    input_dataset = dataiku.Dataset(input_dataset_name)
    output_dataset_name = get_output_names_for_role('output_dataset')[0]
    output_dataset = dataiku.Dataset(output_dataset_name)
    return (input_dataset, output_dataset)


def check_params(params):
    dku_config = DkuConfig()

    dku_config.add_param(
        name="family_name",
        value=params['family_name'],
        checks=[{
            "type": "in",
            "op": ["binomial", "gamma", "gaussian", "inverse_gaussian", "poisson", "negative_binomial", "tweedie"]
        }],
        required=True
    )

    dku_config.add_param(
        name="binomial_link",
        value=params['binomial_link'],
        checks=[{
            "type": "in",
            "op": ["cloglog", "log", "logit", "cauchy", "identity"]
        }],
        required=False
    )

    dku_config.add_param(
        name="gamma_link",
        value=params['gamma_link'],
        checks=[{
            "type": "in",
            "op": ["log", "identity", "inverse_power"]
        }],
        required=False
    )

    dku_config.add_param(
        name="gaussian_link",
        value=params['gaussian_link'],
        checks=[{
            "type": "in",
            "op": ["log", "identity", "inverse_power"]
        }],
        required=False
    )

    dku_config.add_param(
        name="inverse_gaussian_link",
        value=params['inverse_gaussian_link'],
        checks=[{
            "type": "in",
            "op": ["log", "inverse_squared", "identity", "inverse_power"]
        }],
        required=False
    )

    dku_config.add_param(
        name="poisson_link",
        value=params['poisson_link'],
        checks=[{
            "type": "in",
            "op": ["log", "identity"]
        }],
        required=False
    )

    dku_config.add_param(
        name="negative_binomial_link",
        value=params['negative_binomial_link'],
        checks=[{
            "type": "in",
            "op": ["log", "cloglog", "identity", "power"]
        }],
        required=False
    )

    dku_config.add_param(
        name="tweedie_link",
        value=params['tweedie_link'],
        checks=[{
            "type": "in",
            "op": ["log", "power"]
        }],
        required=False
    )

    dku_config.add_param(
        name="alpha",
        value=params['alpha'],
        checks=[{
            "type": "between",
            "op": (0.01, 2)
        }],
        required=False
    )

    dku_config.add_param(
        name="power",
        value=params['power'],
        required=False
    )

    if not isinstance(params['penalty'], list):
        params['penalty'] = [params['penalty']]
    for i, penalty in enumerate(params['penalty']):
        dku_config.add_param(
            name="penalty_" + str(i),
            value=penalty,
            checks=[{
                "type": "sup_eq",
                "op": 0
            }],
            required=True
        )

    dku_config.penalty = [dku_config["penalty_" + str(i)] for i in range(len(params['penalty']))]

    dku_config.add_param(
        name="var_power",
        value=params['var_power'],
        required=False
    )

    dku_config.add_param(
        name="offset_mode",
        value=params['offset_mode'],
        checks=[{
            "type": "in",
            "op": ['BASIC', 'OFFSET', 'EXPOSURE']
        }],
        required=True
    )

    project_key = dataiku.get_custom_variables()["projectKey"]
    project = dataiku.api_client().get_project(project_key)

    datasets = [analysis['inputDataset'] for analysis in project.list_analyses()]

    dku_config.add_param(
        name="training_dataset",
        value=params['training_dataset'],
        checks=[{
            "type": "in",
            "op": datasets
        }],
        required=False
    )
    dataset = dataiku.Dataset(params['training_dataset'], project_key)

    dku_config.add_param(
        name="offset_column",
        value=None if 'offset_column' not in params else params['offset_column'],
        checks=[{
            "type": "in",
            "op": dataset.get_dataframe().columns
        }],
        required=False
    )

    dku_config.add_param(
        name="exposure_column",
        value=None if 'exposure_column' not in params else params['exposure_column'],
        checks=[{
            "type": "in",
            "op": dataset.get_dataframe().columns
        }],
        required=False
    )

    return dku_config
