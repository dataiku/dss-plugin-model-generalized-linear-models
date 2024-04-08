<template>
<BsTab name="Model Training" docTitle="GLM Analyzer" :docIcon="docLogo">
    <BsTabIcon>
        <img :src="firstTabIcon" alt="Target Definition Icon" />
    </BsTabIcon>
    <BsHeader>
        <BsButton
            v-if="!layoutRef?.drawerOpen" flat round class="open-side-drawer-btn" size="15px"
            @click="closeSideDrawer" icon="mdi-arrow-right">
            <BsTooltip>Open sidebar</BsTooltip>
        </BsButton>
    </BsHeader>
    <BsDrawer>
        <h5 class="h5-spacing">Model Parameters</h5>
        <div class="variable-select-container">
            <VariableSelect
                label="Select a Distribution Function"
                :modelValue="selectedDistributionFunctionString"
                :options="distributionOptions"
                @update:modelValue="value => updateModelProperty('selectedDistributionFunctionString', value)"
                helpMessage="Distribution function for GLM "
                style="min-width: 150px">
            </VariableSelect>
            <VariableSelect
                label="Select a Link Function"
                :modelValue="selectedLinkFunctionString"
                :options="linkOptions"
                @update:modelValue="value => updateModelProperty('selectedLinkFunctionString', value)"
                helpMessage="Link function for GLM "
                style="min-width: 150px">
            </VariableSelect>
        </div>
        <h5 class="h5-spacing">Custom Variables</h5>
        <div class="variable-select-container">
        <VariableSelect
            label="Select a Target Variable"
            :modelValue="selectedTargetVariable"
            :options="targetVariablesOptions"
            @update:modelValue="value => selectedTargetVariable = value.value"
            helpMessage="Target Variable for GLM "
            style="min-width: 150px">
        </VariableSelect>
        <VariableSelect
            label="Select an Exposure Variable"
            :modelValue="selectedExposureVariable"
            :options="exposureVariableOptions"
            @update:modelValue="value => selectedExposureVariable = value.value"
            helpMessage="Exposure Variable for GLM "
            style="min-width: 150px">
        </VariableSelect>
        </div>
        <div class="model-name-input-container">
            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
            <input
            v-model="modelName"
            type="text"
            id="modelNameInput"
            placeholder="Enter model name"
            class="model-name-input"
            />
        <q-btn color="primary" class="q-mt-md" label="Train Model" @click="submitVariables"></q-btn>
        
        </div>
        

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
                    <q-toggle
                        label=""
                        v-model="column.isIncluded"
                        @update:modelValue="newValue => updateColumnProperty(index, 'isIncluded', newValue)"
                    ></q-toggle>
                    <span class="column-name">{{ abbreviateColumnName(column.name) }}</span>

 
                    <div class="q-gutter-sm row items-center">
                        <q-radio v-model="column.type" val="numerical" label="Numerical" />
                    </div>
                    <div class="q-gutter-sm row items-center">
                        <q-radio v-model="column.type" val="categorical" label="Categorical" />
                    </div>
                    <!-- <VariableSelect
                        label="Column Type"
                        :modelValue="column.type"
                        :options="typeOptions"
                        @update:modelValue="newValue => updateColumnProperty(index, 'type', newValue)"
                        helpMessage="Does the column contain categorical or numerical data?"
                        style="min-width: 150px">
                    </VariableSelect> -->
                    <!-- <VariableSelect
                        label="Preprocessing"
                        :modelValue="column.preprocessing"
                        :options="preprocessingOptions"
                        @update:modelValue="newValue => updatePreprocessing(index, newValue)"
                        helpMessage="Preprocessing Method"
                        style="min-width: 150px">
                    </VariableSelect> -->
            </div>
        </q-card>
    </BsContent>
    
</BsTab>

</template>

<script lang="ts">
type ColumnPropertyKeys = 'isIncluded' | 'role' | 'type' | 'preprocessing';
type UpdatableProperties = 'selectedDatasetString' | 'selectedDistributionFunctionString' | 'selectedLinkFunctionString';
interface Column {
        name: string;
        isIncluded: boolean | { label: string; value: boolean };
        role: string | { label: string; value: string };
        type: string | { label: string; value: string };
        preprocessing: string | { label: string; value: string };
        }
interface SelectionOption {
label: string;
value: string; 
}
interface AccType {
[key: string]: {
role: string;
type: string;
processing: string;
included: boolean;
};
}
import { defineComponent } from "vue";
import VariableSelect from './VariableSelect.vue';
import EmptyState from './EmptyState.vue';
import { BsTab, BsTabIcon, BsLayoutDefault, BsHeader, BsButton, BsDrawer, BsContent, BsTooltip } from "quasar-ui-bs";
import docLogo from "../assets/images/doc-logo-example.svg";
import firstTabIcon from "../assets/images/first-tab-icon.svg";
import { API } from '../Api';
import { QRadio } from 'quasar';

export default defineComponent({
components: {
    VariableSelect,
    EmptyState,
    BsTab,
    BsTabIcon,
    BsHeader,
    BsButton,
    BsDrawer,
    BsContent,
    BsTooltip,
    QRadio

},
props: [],
data() {
    return {    
        modelName: "",   
        errorMessage: "", 
        selectedDatasetString: "",
        selectedTargetVariable: "",
        selectedExposureVariable: "",
        selectedDistributionFunctionString: { label: 'Gaussian', value: 'Gaussian' } as SelectionOption,
        selectedLinkFunctionString:{ label: 'Log', value: 'Log' }  as SelectionOption,
        datasetsString: [] as string[],
        chartData: [],  
        layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
        firstTabIcon,
        docLogo,
        distributionOptions: [
            { label: 'Binomial', value: 'Binomial' },
            { label: 'Gamma', value: 'Gamma' },
            { label: 'Gaussian', value: 'Gaussian' },
            { label: 'Inverse Gaussian', value: 'Inverse Gaussian' },
            { label: 'Poisson', value: 'Poisson' },
            { label: 'Negative Binomial', value: 'Negative Binomial' },
            { label: 'Tweedie', value: 'Tweedie' },
        ],
        linkOptions: [
            { label: 'CLogLog', value: 'CLogLog' },
            { label: 'Log', value: 'Log' },
            { label: 'Logit', value: 'Logit' },
            { label: 'Cauchy', value: 'Cauchy' },
            { label: 'Identity', value: 'Identity' },
            { label: 'Power', value: 'Power' },
            { label: 'Inverse Power', value: 'Inverse Power' },
            { label: 'Inverse Squared', value: 'Inverse Squared' },
        ],
        typeOptions: [
            { label: 'Categorical', value: 'categorical' },
            { label: 'Numerical', value: 'numerical' },
        ],
        preprocessingOptions: [
            { label: 'Dummy Encode', value: 'CUSTOM' },
            { label: 'Standard Rescaling', value: 'REGULAR' },
        ],
        roleOptions: [
            {label: 'Exposure', value: 'Exposure'},
            {label: 'Variable', value: 'Variable'},
        ],
        datasetColumns: [] as Column[], // Populate this based on your actual data
    };
},
computed:{
    targetVariablesOptions(){
        return this.datasetColumns.map(column=>{
            return {label:column.name,value:column.name};
        });
        },
    exposureVariableOptions(){
        return this.datasetColumns
        .filter(column => {
            return ((column.role as { label: string; value: string }).value !== 'Target');
            })
            
            .map(column=>{
            return {label:column.name, value:column.name};
            });
        },
filteredColumns() {
    return this.datasetColumns.filter(column =>
        (typeof column.role === 'object' ? column.role.value : column.role) !== 'Target' &&
        (typeof column.role === 'object' ? column.role.value : column.role) !== 'Exposure');

}
},
watch: {

    selectedTargetVariable(newValue, oldValue) {
        console.log(` Attempting to change selectedTargetVariable changed from ${oldValue} to ${newValue}`);
        this.datasetColumns.forEach(column => {
            if (column.name === newValue) {
                // Set the role of the selected target variable to 'Target'
                column.role = { label: 'Target', value: 'Target' };
            } else {
                // Reset role for non-target columns if necessary
                column.role = { label: 'Variable', value: 'Variable' }; // Or any default value you prefer
            }
        });
    },
    selectedExposureVariable(newValue, oldValue) {
        console.log(` Attempting to change selectedExposureVariable changed from ${oldValue} to ${newValue}`);
        this.datasetColumns.forEach(column => {
            if (column.name === newValue) {
                // Set the role of the selected target variable to 'Target'
                column.role = { label: 'Exposure', value: 'Exposure' };
            } else if ((column.role as { value: string }).value !== 'Target') {
                // Reset role for non-target columns if necessary
                column.role = { label: 'Variable', value: 'Variable' }; // Or any default value you prefer
            }
        });
    },
    datasetColumns: {
    handler(newVal, oldVal) {
        console.log('datasetColumns changed:', newVal);
        this.updateDatasetColumnsPreprocessing();
    },
    deep: true
    }   
    
},
methods: {
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
                preprocessing = { label: 'Dummy Encode', value: 'CUSTOM' };
            } else if (column.type === "numerical") {
                preprocessing = { label: 'Standard Rescaling', value: 'REGULAR' };
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
        const maxLength = 15; // Maximum length of column name
        if (name.length > maxLength) {
        return `${name.substring(0, maxLength - 1)}...`; // 
        }
        return name; // Return the original name if it's short enough
    },
    closeSideDrawer() {
        if (this.layoutRef) {
            this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
        }
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
    updateColumnProperty(columnIndex:number, property: ColumnPropertyKeys, value: any) {
        const column = this.datasetColumns[columnIndex];
        if (column) {
                column[property] = value;
            }
            // Trigger a Vue reactivity update
            this.datasetColumns.splice(columnIndex, 1, column);
        },
    async submitVariables() {
        if (!this.validateSubmission()) {
      // If validation fails, stop execution
        return;
        }
        // Define modelParameters outside of the reduce call to ensure it's accessible later
        const modelParameters = {
            model_name: this.modelName,
            distribution_function: this.selectedDistributionFunctionString.value,
            link_function: this.selectedLinkFunctionString.value,
        };

        // Reduce function to construct Variables object    
        const variableParameters = this.datasetColumns.reduce<AccType>((acc, { name, role, type, preprocessing, isIncluded }) => {
        acc[name] = {
            role: typeof role === 'object' ? role.value : role,
            type: typeof type === 'object' ? type.value : type,
            processing: typeof preprocessing === 'object' ? preprocessing.value : preprocessing,
            included: typeof isIncluded === 'object' ? isIncluded.value : isIncluded,
        };
        return acc;
        }, {});
        // Now modelParameters is available to be included in payload
        const payload = {
            model_parameters: modelParameters,
            variables: variableParameters
        };
        try {
            console.log("Payload:", payload);
            const modelUID = await API.trainModel(payload);
            // Handle successful submission here
        } catch (error) {
            console.error('Error submitting variables:', error);
            // Handle errors here
        }
    },

    async getDatasetColumns() {
        try {
        const response = await API.getDatasetColumns();

        console.log("Datasets:", response.data);
        this.datasetColumns = response.data.map((columnName: string) => ({
            name: columnName,   
            isIncluded: true,
            role: {label: 'Variable', value: 'Variable'},
            type: 'categorical',
            preprocessing: { label: 'Dummy Encode', value: 'CUSTOM' }
        }));
        console.log("First assignment:", this.datasetColumns);
        } catch (error) {
            console.error('Error fetching datasets:', error);
            this.datasetColumns = [];
        }
    },  
},
async mounted() {
    this.layoutRef = this.$refs.layout as InstanceType<typeof BsLayoutDefault>;
    const savedDistributionFunction = localStorage.getItem('DistributionFunction');
    const savedLinkFunction = localStorage.getItem('linkFunction');
    await this.getDatasetColumns();
},
emits: ['update:modelValue']
})
</script>   
<style scoped>
.row-spacing {
margin-bottom: 20px; /* Adjust this value as needed */
}
.column-management {
display: flex;
align-items: center; /* Align items vertically */
gap: 20px; /* Spacing between each item */
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
</style>


