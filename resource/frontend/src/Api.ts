import axios from "./api/index";
import type { AxiosError } from 'axios';

interface ErrorResponse {
    error: string;
}

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

interface BaseValue {
    variable: string;
    base_level: string;
}

interface ModelPoint {
    id: string;
    name: string;
}

interface ModelVariablePoint {
    id: string;
    name: string;
    variable: string;
    trainTest: boolean;
    rescale: boolean;
}

interface ModelNbBins {
    id: string;
    name: string;
    nbBins: number;
    trainTest: boolean;
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
interface ExcludedColumns {
    target_column: string;
    exposure_column: string;
}
interface MLTaskParams {
    target_column: string;
    exposure_column: string;
    distribution_function: string;
    link_function: string;
    elastic_net_penalty: number;
    l1_ratio: number;
    params: {
        [key: string]: {
            role: string;
            type: string;
            handling: string | null;
            chooseBaseLevel: boolean;
            baseLevel: string;
        }
    };
}


export let API = {
    getLatestMLTaskParams: (data:any) => axios.post<MLTaskParams>("/api/get_latest_mltask_params", data),
    getExcludedColumns: () => axios.get<ExcludedColumns>("/api/get_excluded_columns"),
    getData: (data: ModelPoint) => axios.post<DataPoint[]>("/api/data", data),
    getBaseValues: (data: ModelPoint) => axios.post<BaseValue[]>("/api/base_values", data),
    getLiftData: (data: ModelNbBins) => axios.post<LiftDataPoint[]>("/api/lift_data", data),
    updateData: (data: FeatureNbBin) => axios.post<DataPoint[]>("/api/update_bins", data),
    getRelativities: (data: ModelPoint) => axios.post<RelativityPoint[]>("/api/relativities", data),
    getModels: () => axios.get<ModelPoint[]>("/api/models"),
    getVariables: (data: ModelPoint) => axios.post<VariablePoint[] | ErrorPoint>("/api/variables", data),
    getProjectDataset: () => axios.get<string[]>("/api/get_project_dataset", {}),
    getDatasetColumns: () => axios.get("/api/get_dataset_columns", {}),
    getTrainDatasetColumnNames: () => axios.get("/api/get_train_dataset_column_names", {}),
    trainModel: (payload: any) => 
        axios.post<string[]>("/api/train_model", payload)
        .catch((error: AxiosError<ErrorResponse>) => {
            throw error;
        }),
    getModelComparisonData: (data: any) => axios.post<ModelComparisonDataPoint[]>("/api/get_model_comparison_data", data),
    getModelMetrics: (data: any) => axios.post<ModelMetricsDataPoint>("/api/get_model_metrics", data),
    exportModel: (model: ModelPoint) => axios.post<Blob>("/api/export_model", model),
    exportVariableLevelStats: (model: ModelPoint) => axios.post<Blob>("/api/export_variable_level_stats", model),
    exportOneWay: (model: ModelVariablePoint) => axios.post<Blob>("/api/export_one_way", model),
    getVariableLevelStats: (data: ModelPoint) => axios.post<VariableLevelStatsPoint[]>("/api/get_variable_level_stats", data),
}

