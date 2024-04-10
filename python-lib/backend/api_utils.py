def format_models(global_dku_mltask):
    list_ml_id = global_dku_mltask.get_trained_models_ids()
    models = []
    for ml_id in list_ml_id:
        model_details = global_dku_mltask.get_trained_model_details(ml_id)
        model_name = model_details.get_user_meta()['name']
        models.append({"id": ml_id, "name": model_name})
    return models