<template>
    <div>
    <q-card-section>
                <h5>Feature Handling</h5>
            </q-card-section>
            <q-card class="q-pa-xl">
                <div v-for="(column, index) in filteredColumns" class="column-management row-spacing">
                    <div class="column-name-container">
                        <h6 class="column-name">{{ store.abbreviateColumnName(column.name) }}</h6>
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
                :initial-interactions="store.previousInteractions"
                 @update:interactions="store.updateInteractions"
            />
            </q-card>
        </div>
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
            console.log(this.store.datasetColumns);
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
        
        
    }
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