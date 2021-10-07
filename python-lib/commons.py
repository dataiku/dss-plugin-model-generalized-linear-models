import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role

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