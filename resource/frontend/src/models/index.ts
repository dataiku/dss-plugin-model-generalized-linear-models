export type DataPoint = { 
    definingVariable: string;
    Category: string;
    Value: number;
    observedAverage: number;
    fittedAverage: number;
    baseLevelPrediction: number;
}

export type ColumnInput = {
    column: string;
    baseLevel: string;
    options: Array<string>;
}

export type LiftDataPoint = { 
    Category: string;
    Value: number;
    observedAverage: number;
    fittedAverage: number;
}

export type RelativityPoint = {
    variable: string;
    category: string;
    relativity: number;
}

export type VariableLevelStatsPoint = {
    variable: string;
    value: string;
    coefficient: number;
    standard_error: number;
    standard_error_pct: number;
    weight: number;
    weight_pct: number;
    relativity: number;
}

export type ModelPoint = { 
    id: string;
    name: string;
}

export type Interaction = { 
    first: string;
    second: string;
}

export type BaseValue = {
    variable: string;
    base_level: string;
}

export type ModelVariablePoint = { 
    id: string;
    name: string;
    variable: string;
    trainTest: boolean;
}

export type ModelNbBins = { 
    id: string;
    name: string;
    nbBins: number;
    trainTest: boolean;
}
export type ModelTrainPoint = { 
    id: string;
    name: string;
    trainTest: boolean;
}

export type VariablePoint = {
    variable: string;
    isInModel: boolean;
    variableType: string;
}

export type ErrorPoint = {
    error: string;
}

export type ModelMetricsDataPoint = {
    AIC: number;
    BIC: number;
    Deviance: number;
}

export type ModelMetrics = {
    [models: string]: ModelMetricsDataPoint;
}

export type AccType = {
    [key: string]: {
    role: string;
    type: string;
    processing: string;
    included: boolean;
    base_level: string;
    };
}

export type APIResponse = {
    data: MLTaskParams;
    }   
    interface MLTaskParams {
        params: {
            [key: string]: {
                role: string;
                type: string;
                handling: string;
                baseLevel?: string;
            }
        };
        target_column: string;
        exposure_column: string;
        distribution_function: string;
        link_function: string;
        elastic_net_penalty?: number;
        l1_ratio?: number;
        interactions?: Array<{
            first: string;
            second: string;
        }>;
}

export type Column = {
    name: string;
    isIncluded: boolean;
    role: string;
    type: string;
    preprocessing: string;
    baseLevel: string;
    options: Array<string>;
}


export function isErrorPoint(obj: any): obj is ErrorPoint {
    return typeof obj === 'object' && obj !== null && 'error' in obj && typeof obj.error === 'string';
}