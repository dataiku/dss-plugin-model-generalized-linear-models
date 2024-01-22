import axios from "./api/index";

interface HelloResponse {
    key: string;
}

interface DataRecord {
    Category: string;
    Value: number;
}

export let API = {
    getHello: () => axios.get<HelloResponse>("/api/hello"),
    getData: () => axios.get<DataRecord[]>("/api/data"),
}