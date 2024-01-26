export type DataPoint = { 
    definingVariable: string;
    Category: string;
    Value: number;
    observedAverage: number;
    fittedAverage: number;
    baseLevelPrediction: number;
}

export type ModelPoint = { 
    id: string;
}