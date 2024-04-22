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
    variable_values: any;
    exposure: number;
    Model_1_fittedAverage: number;
    Model_2_fittedAverage: number;
    observed_average: number;
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


export let API = {
    getData: (data: ModelPoint) => axios.post<DataPoint[]>("/api/data", data),
    getLiftData: (data: ModelPoint) => axios.post<LiftDataPoint[]>("/api/lift_data", data),
    updateData: (data: FeatureNbBin) => axios.post<DataPoint[]>("/api/update_bins", data),
    getRelativities: (data: ModelPoint) => axios.post<RelativityPoint[]>("/api/relativities", data),
    getModels: () => axios.get<ModelPoint[]>("/api/models"),
    getVariables: (data: ModelPoint) => axios.post< []>("/api/variables", data),
    getProjectDataset: () => axios.get<string[]>("/api/get_project_dataset", {}),
    getDatasetColumns: () => axios.get("/api/get_dataset_columns", {}),
    trainModel: (payload: any) => axios.post<string[]>("/api/train_model",payload),
    getModelComparisonData: (data: any) => axios.post<ModelComparisonDataPoint[]>("/api/get_model_comparison_data", data),
    getModelMetrics: (data: any) => axios.post<ModelMetrics>("/api/get_model_metrics", data),
    exportModel: () => axios.get<Blob>("/api/export_model"),
    getVariableLevelStats: (data: ModelPoint) => axios.post<VariableLevelStatsPoint[]>("/api/get_variable_level_stats", data),
}

