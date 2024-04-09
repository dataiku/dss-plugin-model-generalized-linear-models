export type DataPoint = { 
    definingVariable: string;
    Category: string;
    Value: number;
    observedAverage: number;
    fittedAverage: number;
    baseLevelPrediction: number;
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

export type VariablePoint = {
    variable: string;
    isInModel: boolean;
    variableType: string;
}