import axios from "./api/index";

interface DataPoint {
    definingVariable: string;
    Category: string;
    Value: number;
    observedAverage: number;
    fittedAverage: number;
    baseLevelPrediction: number;
}

interface ModelPoint {
    id: string;
}

export let API = {
    getData: (data: ModelPoint) => axios.post<DataPoint[]>("/api/data", data),
    getModels: () => axios.get<ModelPoint[]>("/api/models"),
}