import { defineStore } from "pinia";
import { API } from "../Api";
import type { DataPoint, ModelPoint, RelativityPoint, VariablePoint } from '../models';

export const useStore = defineStore("WebAppStore", {
    state: () => ({
        chartData: [] as DataPoint[],
        allData: [] as DataPoint[],
        relativitiesData: [] as RelativityPoint[],
        relativitiesTable: [] as RelativityPoint[],
        models: [] as ModelPoint[],
        selectedModel: {} as ModelPoint,
        modelsString: [] as string[],
        selectedModelString: "",
        variablePoints: [] as VariablePoint[],
        allVariables: [] as String[],
        variables: [] as VariablePoint[],
        selectedVariable: {} as VariablePoint,
        relativities: [],
        relativitiesColumns: [],
        inModelOnly: true,
        includeSuspectVariables: true,
    }),
    getters: {
    },
    actions: {
        async getModels() {
            API.getModels().then((data: any) => {
                this.models = data.data;
                this.modelsString = this.models.map(item => item.name);
              });
        },
    }
});
