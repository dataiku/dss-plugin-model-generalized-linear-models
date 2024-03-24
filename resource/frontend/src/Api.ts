import axios from "./api/index";

interface DataPoint {
    definingVariable: string;
    Category: string;
    Value: number;
    observedAverage: number;
    fittedAverage: number;
    baseLevelPrediction: number;
}

interface RelativityPoint {
    variable: string;
    category: string;
    relativity: number;
}

interface ModelPoint {
    id: string;
    name: string;
}

interface FeatureNbBin {
    feature: string;
    nbBin: number;
}

interface VariablePoint {
    variable: string;
    isInModel: boolean;
    variableType: string;
}

interface DatasetName{
    name: string;
}
export let API = {
    getData: (data: ModelPoint) => axios.post<DataPoint[]>("/api/data", data),
    updateData: (data: FeatureNbBin) => axios.post<DataPoint[]>("/api/update_bins", data),
    getRelativities: (data: ModelPoint) => axios.post<RelativityPoint[]>("/api/relativities", data),
    getModels: () => axios.get<ModelPoint[]>("/api/models"),
    getVariables: (data: ModelPoint) => axios.post< []>("/api/variables", data),
    getProjectDataset: () => axios.get<string[]>("/api/get_project_dataset", {}),
    getDatasetColumns: () => axios.get("/api/get_dataset_columns", {}),
    trainModel: (payload: any) => axios.post<string[]>("/api/train_model",payload),
}