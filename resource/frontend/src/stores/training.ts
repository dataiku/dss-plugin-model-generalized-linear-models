import { defineStore } from "pinia";
import { API } from "../Api";
import { useLoader } from "../composables/use-loader";
import { useNotification } from "../composables/use-notification";
import { isErrorPoint } from '../models';
import type { 
  ModelPoint, VariablePoint, 
  ModelMetricsDataPoint,  
} from '../models';
import { isAxiosError } from 'axios'; 
import type { AxiosError, AxiosResponse } from 'axios';  

type UpdatableProperties = 'selectedDatasetString' | 'selectedDistributionFunctionString' | 'selectedLinkFunctionString';

interface ErrorResponse {
    error: string;
}

interface AccType {
    [key: string]: {
    role: string;
    type: string;
    processing: string;
    included: boolean;
    base_level: string;
    };
}

interface Column {
    name: string;
    isIncluded: boolean;
    role: string;
    type: string;
    preprocessing: string;
    baseLevel: string;
    options: Array<string>;
}

interface Interaction {
    first: string;
    second: string;
}

export const useTrainingStore = defineStore("TrainingStore", {
    state: () => ({
        modelName: "",   
        errorMessage: "", 
        selectedModelString: "",
        models: [] as ModelPoint[],
        modelsString: [] as string[],
        interactions: [] as Interaction[],
        selectedDatasetString: "",
        selectedTargetVariable: "",
        selectedExposureVariable: "",
        selectedDistributionFunctionString: 'Gaussian' as string,
        selectedLinkFunctionString: 'Log' as string,
        datasetsString: [] as string[],
        chartData: [],  
        selectedElasticNetPenalty: 0 as number,
        selectedL1Ratio: 0 as number,
        previousInteractions: [] as Array<{first: string, second: string}>, 
        distributionOptions: ['Binomial',
            'Gamma',
            'Gaussian',
            'Inverse Gaussian',
            'Poisson',
            'Negative Binomial', 
            'Tweedie',
        ],
        linkOptions: [
            'CLogLog',
            'Log',
            'Logit',
            'Cauchy',
            'Identity',
            'Power',
            'Inverse Power',
            'Inverse Squared'
        ],
        typeOptions: [
            'Categorical',
            'Numerical'
        ],
        preprocessingOptions: [
            'Dummy Encode',
            'Standard Rescaling',
        ],
        datasetColumns: [] as Column[], // Populate this based on your actual data
        loading: false as boolean
    }),
    actions: {
        updateInteractions(newInteractions: Array<string>) {
            // Convert the formatted strings back to interaction objects
            this.previousInteractions = newInteractions.map(interaction => {
                const [first, second] = interaction.split(':');
                return { first, second };
            });
        },
        async fetchExcludedColumns() {
        try {
        const excludedColumnsResponse = await API.getExcludedColumns();
        const { target_column, exposure_column } = excludedColumnsResponse.data;
        
        // Update selectedTargetVariable and selectedExposureVariable
        this.selectedTargetVariable = target_column;
        this.selectedExposureVariable = exposure_column;
        
        // Update the roles in datasetColumns
        this.datasetColumns.forEach(column => {
            if (column.name === target_column) {
            column.role = 'Target';
            } else if (column.name === exposure_column) {
            column.role = 'Exposure';
            } else {
            column.role = 'Variable';
            }
        });
        } catch (error) {
        console.error('Error fetching excluded columns:', error);
        }
    },

    async updateModelString(value: string) {
          this.loading = true;
          this.selectedModelString = value;
          const model = this.models.filter( (v: ModelPoint) => v.name==value)[0];
          this.loading = false;
        },
        notifyError(msg: string) {
            useNotification("negative", msg);
        },
        handleError(msg: any) {
            this.loading = false;
            console.error(msg);
            this.notifyError(msg);
        },
    validateSubmission() {
        this.errorMessage = ''; // Reset error message before validation
        if (!this.modelName) {
        this.errorMessage = 'Please enter a model name.';
        console.log('Error Message:', this.errorMessage);

        return false;
        }
        if (!this.selectedTargetVariable) {
        this.errorMessage = 'Please select a target variable.';
        return false;
        }
        return true; // Validation passed
    },
    updateDatasetColumnsPreprocessing() {
        const updatedColumns = this.datasetColumns.map(column => {
            let preprocessing;
            if (column.type === "categorical") {
                preprocessing = 'Dummy Encode';
            } else if (column.type === "numerical") {
                preprocessing = 'Standard Rescaling';
            } else {
                // Preserve the existing preprocessing if the type doesn't match
                preprocessing = column.preprocessing;
            }

            // Only update preprocessing if it's different to avoid infinite loops
            if (JSON.stringify(column.preprocessing) !== JSON.stringify(preprocessing)) {
                return { ...column, preprocessing };
            } else {
                return column;
            }
        });

        // Check if the update is necessary to avoid unnecessary reactivity triggering
        if (JSON.stringify(this.datasetColumns) !== JSON.stringify(updatedColumns)) {
            this.datasetColumns = updatedColumns;
        }
    },
    abbreviateColumnName(name:string) {
        const maxLength = 12 ; // Maximum length of column name
        if (name.length > maxLength) {
        return `${name.substring(0, maxLength - 1)}...`; // 
        }
        return name; // Return the original name if it's short enough
    },
    updateModelProperty(property: UpdatableProperties, value: any): void{
        this[property] = value;
        localStorage.setItem(property, JSON.stringify(value));
        console.log(`updateModelProperty: Updating ${String(property)} to ${JSON.stringify(value)}`);
    },
    updatePreprocessing(index: number, newValue: any) {
        const column = this.datasetColumns[index];
        if (column) {
            column.preprocessing = newValue;
            // Since Vue 2 doesn't reactively update arrays on index, force update
            this.datasetColumns[index] = column;
        }
    },
    updateType(index:number, value: any) {
        const column = this.datasetColumns[index];
        if (column) {
                column.type = value;
            }
            // Trigger a Vue reactivity update
            this.datasetColumns[index] = column;
        },  
        async getDatasetColumns(model_value = null) {
            this.loading = true;
            console.log(model_value);
            if (model_value) {
                console.log("model_id parameter provided:", model_value);
                this.datasetColumns = []
                try {
                        const response = await API.getDatasetColumns();
                        this.selectedModelString = model_value;

                        const model = this.models.filter((v: ModelPoint) => v.name == model_value)[0];
                        console.log("Filtered model:", model);
                        console.log("Making request with model Id :", model);

                        const paramsResponse = await API.getLatestMLTaskParams(model)  as APIResponse;
                        console.log("API.getLatestMLTaskParams response:", paramsResponse);

                        const params = paramsResponse.data.params;
                        console.log("Extracted params:", params);

                        const responseColumns = response.data.map((column: ColumnInput) => column.column);
                        console.log("responseColumns:", responseColumns);

                        const paramsColumns = Object.keys(params);
                        console.log("paramsColumns:", paramsColumns);
                        
                        this.previousInteractions = paramsResponse.data.interactions 
                            ? paramsResponse.data.interactions.map(interaction => ({
                                first: interaction.first,
                                second: interaction.second
                            }))
                            : [];
                        console.log("Interaction recieved in parent", this.previousInteractions)
                        this.selectedDistributionFunctionString = paramsResponse.data.distribution_function;
                        this.selectedLinkFunctionString = paramsResponse.data.link_function;
                        this.selectedElasticNetPenalty = paramsResponse.data.elastic_net_penalty ? paramsResponse.data.elastic_net_penalty : 0;
                        this.selectedL1Ratio = paramsResponse.data.l1_ratio ? paramsResponse.data.l1_ratio : 0;
                        
                        
                        console.log("paramsResponse:", paramsResponse.data);
                        this.datasetColumns = response.data.map((column: ColumnInput) => {
                            const columnName = column.column;
                            const options = column.options;
                            const param = params[columnName];
                            const isTargetColumn = columnName === paramsResponse.data.target_column;
                            const isExposureColumn = columnName === paramsResponse.data.exposure_column;
                            
                            // Set the selected target variable if this column is the target column
                            if (isTargetColumn) {
                                this.selectedTargetVariable = columnName;
                            }

                            // Set the selected exposure variable if this column is the exposure column
                            if (isExposureColumn) {
                                this.selectedExposureVariable = columnName;
                            }

                            // Check if the column names match, excluding the specific column
                        const missingColumns = paramsColumns
                            .filter((col: string) => col !== this.selectedExposureVariable)
                            .filter((col: string) => !responseColumns.includes(col));
                        console.log("missingColumns:", missingColumns);

                        const extraColumns = responseColumns
                            .filter((col: string) => col !== this.selectedExposureVariable)
                            .filter((col: string) => !paramsColumns.includes(col));
                        console.log("extraColumns:", extraColumns);

                        
                        if (missingColumns.length > 0 || extraColumns.length > 0) {
                            let errorMessage = "Column mismatch: Your training dataset does not contain the same variables as the model you requested.\n";
                            if (missingColumns.length > 0) {
                                errorMessage += `Missing columns: ${missingColumns.join(", ")}\n`;
                            }
                            if (extraColumns.length > 0) {
                                errorMessage += `Extra columns: ${extraColumns.join(", ")}`;
                            }
                            this.handleError(errorMessage);
                            return;
                        }
                            return {
                                name: columnName,
                                isIncluded: isTargetColumn || isExposureColumn || param.role !== 'REJECT',
                                role: isTargetColumn ? 'Target' : (isExposureColumn ? 'Exposure' : (param.role || 'REJECT')),
                                type: param.type ? (param.type === 'NUMERIC' ? 'numerical' : 'categorical') : 'categorical',
                                preprocessing: param.handling ? (param.handling === 'DUMMIFY' ? 'Dummy Encode' : param.handling) : 'Dummy Encode',
                                options: options,
                                baseLevel: param.baseLevel ? param.baseLevel : column.baseLevel
                            };
                        });

                    } catch (error) {
                        console.error("Error fetching data:", error);
                    }finally {
                            this.loading = false;
                        }
                    

            } 
            else {
                console.log("No model id provided:");
                try {
                    const response = await API.getDatasetColumns();

                    this.datasetColumns = response.data.map((column: ColumnInput) => ({
                        name: column.column,
                        isIncluded: false,
                        role: 'Variable',
                        type: 'categorical',
                        preprocessing: 'Dummy Encode',
                        options: column.options,
                        baseLevel: column.baseLevel
                    }));

                console.log("First assignment");
                await this.fetchExcludedColumns();
                } catch (error) {
                    console.error('Error fetching datasets:', error);
                    this.datasetColumns = [];
                }
            }
            this.loading = false;
            }
    },
  });