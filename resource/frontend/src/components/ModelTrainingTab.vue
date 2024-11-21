<template>
    <BsTab name="Model Training" docTitle="GLM Analyzer" :docIcon="docLogo">
        <BsTabIcon>
            <img :src="trainingIcon" alt="Target Definition Icon" />
        </BsTabIcon>
        <!-- <BsHeader>
            <BsButton
                v-if="!layoutRef?.drawerOpen" flat round class="open-side-drawer-btn" size="15px"
                @click="closeSideDrawer" icon="mdi-arrow-right">
                <BsTooltip>Open sidebar</BsTooltip>
            </BsButton>
        </BsHeader> -->
        <BsDrawer>
            
            <!-- <BsButton
                flat
                round
                class="close-side-drawer-btn"
                size="15px"
                @click="closeSideDrawer"
                icon="mdi-arrow-left">
                <BsTooltip>Close sidebar</BsTooltip>
            </BsButton> -->
        
        </BsDrawer>
        <BsContent>
            
        </BsContent>
    
    </BsTab>
    
    </template>
    
    <script lang="ts">
    import { defineComponent } from "vue";
    import type { ErrorPoint } from '../models';
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
            errorMessage: "" as string
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
                this.store.updateDatasetColumnsPreprocessing();
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
        this.store.loading = true;
        if (!this.store.validateSubmission()) {
      // If validation fails, stop execution
        return;
        }
        // Define modelParameters outside of the reduce call to ensure it's accessible later
        const modelParameters = {
            model_name: this.store.modelName,
            distribution_function: this.store.selectedDistributionFunctionString,
            link_function: this.store.selectedLinkFunctionString,
            elastic_net_penalty: this.store.selectedElasticNetPenalty,
            l1_ratio: this.store.selectedL1Ratio
        };

        // Reduce function to construct Variables object    
        const variableParameters = this.store.datasetColumns.reduce<AccType>((acc, { name, role, type, preprocessing, isIncluded, baseLevel }) => {
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
        interaction_variables: this.store.previousInteractions.map(interaction => ({
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
            const axiosError = error as AxiosError<ErrorPoint>;
            
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

        this.store.notifyError(this.errorMessage);
    } finally {
        this.updateModels = !this.updateModels;
        this.$emit("update-models", this.updateModels);
        this.store.loading = false;
    }
    },
    },
    async mounted() {
        API.getModels().then((data: any) => {
            this.store.models = data.data;
            this.store.modelsString = this.store.models.map(item => item.name);
            console.log("Models load are", this.store.models)
          });
        this.layoutRef = this.$refs.layout as InstanceType<typeof BsLayoutDefault>;
        const savedDistributionFunction = localStorage.getItem('DistributionFunction');
        const savedLinkFunction = localStorage.getItem('linkFunction');
        await this.store.getDatasetColumns();
    
        
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