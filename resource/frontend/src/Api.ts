import axios from "./api/index";

interface DataPoint {
    definingVariable: string;
    Category: string;
    Value: number;
    observedAverage: number;
    fittedAverage: number;
    baseLevelPrediction: number;
}

interface LiftDataPoint {
    Category: string;
    Value: number;
    observedAverage: number;
    fittedAverage: number;
}
interface ModelMetricsDataPoint {
    AIC: number;
    BIC: number;
    Deviance: number;
}

interface ModelMetrics {
    models: {
        [models: string]: ModelMetricsDataPoint; // Use an index signature for dynamic keys
    }
}

interface ModelComparisonDataPoint {
    definingVariable: any;
    Category: any;
    model_1_observedAverage: any;
    model_1_fittedAverage: any;
    Value: number;
    model1_baseLevelPrediction: any;
    model_2_observedAverage: any;
    model_2_fittedAverage: any;
    model2_baseLevelPrediction: any;
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

interface ModelTrainPoint {
    id: string;
    name: string;
    trainTest: boolean;
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

interface DatasetName {
    name: string;
}

interface VariableLevelStatsPoint {
    variable: string;
    value: string;
    coefficient: number;
    standard_error: number;
    standard_error_pct: number;
    weight: number;
    weight_pct: number;
    relativity: number;
}

interface ErrorPoint {
    error: string;
}

export let API = {
    getData: (data: ModelTrainPoint) => axios.post<DataPoint[]>("/api/data", data),
    getLiftData: (data: ModelTrainPoint) => axios.post<LiftDataPoint[]>("/api/lift_data", data),
    updateData: (data: FeatureNbBin) => axios.post<DataPoint[]>("/api/update_bins", data),
    getRelativities: (data: ModelPoint) => axios.post<RelativityPoint[]>("/api/relativities", data),
    getModels: () => axios.get<ModelPoint[]>("/api/models"),
    getVariables: (data: ModelPoint) => axios.post<VariablePoint[] | ErrorPoint>("/api/variables", data),
    getProjectDataset: () => axios.get<string[]>("/api/get_project_dataset", {}),
    getDatasetColumns: () => axios.get("/api/get_dataset_columns", {}),
    trainModel: (payload: any) => axios.post<string[]>("/api/train_model", payload),
    getModelComparisonData: (data: any) => axios.post<ModelComparisonDataPoint[]>("/api/get_model_comparison_data", data),
    getModelMetrics: (data: any) => axios.post<ModelMetrics>("/api/get_model_metrics", data),
    exportModel: (model: ModelPoint) => axios.post<Blob>("/api/export_model", model),
    getVariableLevelStats: (data: ModelPoint) => axios.post<VariableLevelStatsPoint[]>("/api/get_variable_level_stats", data),
}

