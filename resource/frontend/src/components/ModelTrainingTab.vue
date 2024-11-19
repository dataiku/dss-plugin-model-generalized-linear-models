<template>
    <BsTab name="Model Training" docTitle="GLM Analyzer" :docIcon="docLogo">
        <BsTabIcon>
            <img :src="trainingIcon" alt="Target Definition Icon" />
        </BsTabIcon>
        <BsHeader>
            <BsButton
                v-if="!layoutRef?.drawerOpen" flat round class="open-side-drawer-btn" size="15px"
                @click="closeSideDrawer" icon="mdi-arrow-right">
                <BsTooltip>Open sidebar</BsTooltip>
            </BsButton>
        </BsHeader>
        <BsDrawer>
            <q-scroll-area style="height: calc(100vh - 100px); max-width: 100%">
            <BsCollapsiblePanel
            title="Model Parameters">
                <div class="variable-select-container">
                <BsLabel
                    label="Load a previous model"
                    info-text="Charts will be generated with respect to this model">
                </BsLabel>
                <BsSelect
                    :modelValue="selectedModelString"
                    :all-options="modelsString"
                    @update:modelValue="value => getDatasetColumns(value)"
                    style="min-width: 250px">
                </BsSelect>
                <BsLabel
                        label="Select a Distribution Function"
                        info-text="Distribution function for GLM"
                ></BsLabel>
                <BsSelect
                    :modelValue="selectedDistributionFunctionString"
                    :all-options="distributionOptions"
                    @update:modelValue="value => updateModelProperty('selectedDistributionFunctionString', value)"
                    style="min-width: 150px">
                </BsSelect>
                <BsLabel
                        label="Select a Link Function"
                        info-text="Link function for GLM"
                ></BsLabel>
                <BsSelect
                    :modelValue="selectedLinkFunctionString"
                    :all-options="linkOptions"
                    @update:modelValue="value => updateModelProperty('selectedLinkFunctionString', value)"
                    style="min-width: 150px">
                </BsSelect>
            </div>
             </BsCollapsiblePanel>
            <BsCollapsiblePanel
            title="Regularization">
            <div class="variable-select-container">
            <BsLabel
                    label="Set the Elastic Net Penalty"
                    info-text="The overall level of regularization"
            ></BsLabel>
            <BsSlider
                v-model="selectedElasticNetPenalty"
                :min="0"
                :step="0.01"
                :max="1000"
                style="min-width: 150px">
            </BsSlider>
            <BsLabel
                    label="Set the L1 Ratio"
                    info-text="l1_ratio = 0 means Ridge (only L2), l1_ratio = 1 means LASSO (only L1)"
            ></BsLabel>
            <BsSlider
                v-model="selectedL1Ratio"
                :min="0"
                :max="1"
                :step="0.01"
                style="min-width: 150px">
            </BsSlider>
    
            </div>
            </BsCollapsiblePanel>
            <BsCollapsiblePanel
            title="Model Training"
            >
            <div class="model-name-input-container">
                <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
                <input
                v-model="modelName"
                type="text"
                id="modelNameInput"
                placeholder="Enter model name"
                class="model-name-input"
                />
            <q-btn 
            color="primary" 
            class="q-mt-md" 
            label="Train Model" 
            @click="submitVariables"></q-btn>
            
            </div>
            </BsCollapsiblePanel>
        </q-scroll-area>
            <BsButton
                flat
                round
                class="close-side-drawer-btn"
                size="15px"
                @click="closeSideDrawer"
                icon="mdi-arrow-left">
                <BsTooltip>Close sidebar</BsTooltip>
            </BsButton>
        
        </BsDrawer>
        <BsContent>
            <q-card-section>
                <h5>Feature Handling</h5>
            </q-card-section>
            <q-card class="q-pa-xl">
                <div v-for="(column, index) in filteredColumns" class="column-management row-spacing">
                    <div class="column-name-container">
                        <h6 class="column-name">{{ abbreviateColumnName(column.name) }}</h6>
                    </div>
                    <div class="checkbox-container">
                        <BsCheckbox v-model="column.isIncluded" label="Include?" class="custom-label-spacing"></BsCheckbox>
                    </div>
                    <div class="radio-group-container">
                        <div class="q-gutter-sm row items-center">
                            <q-radio v-model="column.type as any" val="numerical" label="Numerical" />
                        </div>
                        <div class="q-gutter-sm row items-center">
                            <q-radio v-model="column.type as any" val="categorical" label="Categorical" />
                        </div>
                    </div>
                    <div class="radio-group-container">
                        <div class="q-gutter-sm row items-center">
                            <BsSelect
                                label=""
                                :modelValue="column.baseLevel"
                                :all-options="column.options"
                                @update:modelValue="value => column.baseLevel = value">
                            </BsSelect>
                        </div>
                    </div>
                </div>
                
            </q-card>
            <q-card-section>
                <h5>Variable Interactions</h5>
            </q-card-section>
            <q-card class="q-pa-xl">
            <VariableInteractions
                :filtered-columns="filteredColumns"
                :initial-interactions="previousInteractions"
                 @update:interactions="updateInteractions"
            />
            </q-card>
        </BsContent>
    
    </BsTab>
    
    </template>
    
    <script lang="ts">
    type ColumnPropertyKeys = 'isIncluded' | 'role' | 'type' | 'preprocessing' | 'baseLevel' | 'options';

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
    interface APIResponse {
    data: MLTaskParams;
    }   
    interface TypeWithValue {
      value: string;
    }
    interface Interaction {
        first: string;
        second: string;
    }
    interface Model {
        id: string;
        name: string;
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
    interface ColumnInput {
            column: string;
            baseLevel: string;
            options: Array<string>;
            }
    interface SelectionOption {
    label: string;
    value: string; 
    }
    import { defineComponent } from "vue";
    import type { ModelPoint } from '../models';
    import EmptyState from './EmptyState.vue';
    import { BsTab, BsTabIcon, BsLayoutDefault, BsHeader, BsButton, BsDrawer, BsContent, BsTooltip, BsSlider, BsCard } from "quasar-ui-bs";
    import docLogo from "../assets/images/doc-logo-example.svg";
    import trainingIcon from "../assets/images/training.svg";
    import { API } from '../Api';
    import { QRadio } from 'quasar';
    import { useLoader } from "../composables/use-loader";
    import { useNotification } from "../composables/use-notification";
    import type { AxiosError, AxiosResponse } from 'axios';
    import { isAxiosError } from 'axios';   
    import axios from "../api/index";
    import VariableInteractions from './VariableInteractions.vue'
    import { useTrainingStore } from "../stores/training";
    
    export default defineComponent({
    components: {
        EmptyState,
        VariableInteractions,
        BsTab,
        BsTabIcon,
        BsHeader,
        BsButton,
        BsDrawer,
        BsContent,
        BsTooltip,
        QRadio,
        BsSlider,
        BsCard,
    
    },
    props: [],
    data() {
        return {
            updateModels: false,
            store: useTrainingStore(),
            layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
            trainingIcon,
            docLogo,
        };
    },
    computed:{
        filteredColumns() {
                return this.store.datasetColumns.filter(column =>
                    column.role !== 'Target' &&
                    column.role !== 'Exposure')
            },
    },
    watch: {
        datasetColumns: {
            handler(newVal, oldVal) {
                console.log('datasetColumns changed:', newVal);
                this.updateDatasetColumnsPreprocessing();
            },
            deep: true
        },
        
        loading(newVal) {
            if (newVal) {
                useLoader("Loading...").show();
            } else {
                useLoader().hide();
            }
        },
        
        
    },
    methods: {
        async submitVariables() {
        this.loading = true;
        if (!this.validateSubmission()) {
      // If validation fails, stop execution
        return;
        }
        // Define modelParameters outside of the reduce call to ensure it's accessible later
        const modelParameters = {
            model_name: this.modelName,
            distribution_function: this.selectedDistributionFunctionString,
            link_function: this.selectedLinkFunctionString,
            elastic_net_penalty: this.selectedElasticNetPenalty,
            l1_ratio: this.selectedL1Ratio
        };

        // Reduce function to construct Variables object    
        const variableParameters = this.datasetColumns.reduce<AccType>((acc, { name, role, type, preprocessing, isIncluded, baseLevel }) => {
        acc[name] = {
            role: role,
            type: type.toLowerCase(),
            processing: preprocessing == 'Dummy Encode' ? 'CUSTOM' : 'REGULAR',
            included: isIncluded,
            base_level: baseLevel
        };
        return acc;
        }, {});
        // Now modelParameters is available to be included in payload
        const payload = {
        model_parameters: modelParameters,
        variables: variableParameters,
        interaction_variables: this.previousInteractions.map(interaction => ({
            first: interaction.first,
            second: interaction.second
        }))
};
        try {
            console.log("Payload:", payload);
            const modelUID = await API.trainModel(payload);
            // Handle successful submission here
        } catch (error) {
        if (isAxiosError(error)) {
            const axiosError = error as AxiosError<ErrorResponse>;
            
            if (axiosError.response) {
                console.log('Error response:', axiosError.response);
                console.log('Error response data:', axiosError.response.data);
                console.log('Error response status:', axiosError.response.status);
                console.log('Error response headers:', axiosError.response.headers);

                if (axiosError.response.data && 'error' in axiosError.response.data) {
                    this.errorMessage = axiosError.response.data.error;
                } else {
                    this.errorMessage = `Server error: ${axiosError.response.status}`;
                }
            } else if (axiosError.request) {
                console.log('Error request:', axiosError.request);
                this.errorMessage = 'No response received from the server. Please try again later.';
            } else {
                console.log('Error message:', axiosError.message);
                this.errorMessage = 'An unexpected error occurred while training the model.';
            }
        } else {
            this.errorMessage = 'An unexpected error occurred.';
        }

        this.notifyError(this.errorMessage);
    } finally {
        this.updateModels = !this.updateModels;
        this.$emit("update-models", this.updateModels);
        this.loading = false;
    }
    },
    },
    async mounted() {
        API.getModels().then((data: any) => {
            this.models = data.data;
            this.modelsString = this.models.map(item => item.name);
            console.log("Models load are", this.models)
          });
        this.layoutRef = this.$refs.layout as InstanceType<typeof BsLayoutDefault>;
        const savedDistributionFunction = localStorage.getItem('DistributionFunction');
        const savedLinkFunction = localStorage.getItem('linkFunction');
        await this.getDatasetColumns();
    
        
    },
    emits: ['update:modelValue', 'update-models']
    })
    </script>   
    <style scoped>
    .row-spacing {
    margin-bottom: 20px; /* Adjust this value as needed */
    }
    .column-management {
    display: flex;
    flex-direction: row;
    align-items: center; /* Align items vertically */
    gap: 10px; /* Spacing between each item */
    justify-content: space-between; 
    }
    .form-group {
    display: flex;
    flex-direction: column; /* Stack the label and select vertically */
    margin-bottom: 15px; /* Spacing between each form group */
    }
    
    .form-group label {
    margin-bottom: 5px; /* Space between label and select */
    }
    
    /* If you want the label and dropdown to be on the same line, switch .form-group to row */
    .form-group.row {
    flex-direction: row;
    align-items: center; /* Align items vertically */
    }
    
    .form-group.row label {
    margin-right: 10px; /* Space between label and select, when inline */
    margin-bottom: 0; /* Remove bottom margin when inline */
    }
    
    .form-group.row select {
    flex-grow: 1; /* Let the select take up available space */
    }
    .outline-box {
    border: 2px solid #000; /* Solid black border, adjust as needed */
    padding: 20px; /* Optional: Adds some spacing inside the box */
    margin: 20px 0; /* Optional: Adds some spacing outside the box */
    background-color: #f5f5f5; 
    }
    .close-side-drawer-btn {
    color: var(--interactions-bs-color-interaction-primary, #2b66ff);
    position: absolute;
    top: 7px;
    right: 10px;
    z-index: 1000;
    }
    .open-side-drawer-btn {
    color: var(--interactions-bs-color-interaction-primary, #2b66ff);
    position: relative;
    top: 4px;
    }
    .column-name {
    min-width: 100px; /* Adjust based on your layout */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    }
    .h5-spacing {
    margin-bottom: 10px;
    margin-top: 5px;
    }
    .variable-select-container {
        padding: 20px;
    }
    .model-name-input-container {
      padding: 20px
    }
    
    .model-name-input {
      width: 87%;
      padding: 15px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
    .error-message {
      color: red;
      margin-top: 10px;
    }
    .custom-label-spacing {
        margin-right: 10px; /* Adjust the margin as needed */
        margin-left: 10px; 
        padding: 5px;       /* Adjust padding for better alignment and spacing */
    }
    .radio-group-container {
        margin-left: auto; /* Pushes the container to the right */
        display: flex;
        align-items: center;
        flex: 1;
    }
    
    .checkbox-container {
        margin-left: auto; /* Pushes the container to the right */
        display: flex;
        align-items: left;
    }
    .column-name-container {
        margin-left: auto; /* Pushes the container to the right */
        display: flex;
        align-items: left;
        min-width: 150px;
    }
    </style>