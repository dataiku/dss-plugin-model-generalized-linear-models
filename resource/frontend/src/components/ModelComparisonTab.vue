<template>
<BsTab name="Model Comparison" docTitle="GLM Analyzer" :docIcon="docLogo">
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
        <h5 class="h5-spacing">Model Selection</h5>
        <div class="variable-select-container">
            <VariableSelect
                :modelValue="selectedModelString"
                :options="modelsString"
                @update:modelValue="updateModelString"
                label="Select a Model for Comaprison"
                helpMessage="Model 1"
                style="min-width: 250px">
            </VariableSelect>
            <VariableSelect
                label="Select a Second Model for Comaprison"
                :modelValue="selectedModelTwoString"
                :options="modelsString"
                @update:modelValue="updateModelTwoString"
                helpMessage="Model 2"
                style="min-width: 250px">
            </VariableSelect>
        </div>
        <h5 class="h5-spacing">Variable Analysis</h5>
        <div v-if="isVariableSelectEnabled" class="variable-select-container">
        <VariableSelect
            label="Select a Variable For Investigation"
            :modelValue="selectedVariable"
            :options="datasetColumns"
            @update:modelValue="updateVariableString"
            helpMessage="Target Variable for GLM "
            style="min-width: 150px">
        </VariableSelect>
        </div>
    </BsDrawer>
    <BsContent>
        <EmptyState
                class="tab-content"
                title="Model Comparison"
                subtitle="Select two models in the left to comapre"
                v-if="chartData.length==0"/>
            <div class="tab-content" v-else>
                <ModelComparisonChart
                v-if="selectedVariable"
                    :variableValues="chartData.map(item => item.variable_values)"
                    :model1ClaimFrequency="chartData.map(item => item.model_1_claim_frequency)"
                    :model2ClaimFrequency="chartData.map(item => item.model_2_claim_frequency)"
                    :exposures="chartData.map(item => item.exposure)"
                    :chartTitle="selectedVariable"
                    />
                <BsTable
                    :title="this.ComparisonChartTitle"
                    :rows="tableData"
                    :columns="tableColumns"
                    :globalSearch="false"
                    row-key="model"
                />
            </div>
    </BsContent>
    
</BsTab>

</template>

<script lang="ts">
import { defineComponent } from "vue";
import VariableSelect from './VariableSelect.vue';
import EmptyState from './EmptyState.vue';
import { BsTab, BsTabIcon, BsLayoutDefault, BsHeader, BsButton, BsDrawer, BsContent, BsTooltip ,BsTable,} from "quasar-ui-bs";
import docLogo from "../assets/images/doc-logo-example.svg";
import firstTabIcon from "../assets/images/first-tab-icon.svg";
import { API } from '../Api';
import ModelComparisonChart from './ModelComparisonChart.vue'

export default defineComponent({
components: {
    VariableSelect,
    ModelComparisonChart,
    EmptyState,
    BsTab,
    BsTabIcon,
    BsHeader,
    BsButton,
    BsDrawer,
    BsContent,
    BsTooltip
},
props: [],
data() {
    return {    
        datasetsString: [] as string[],
        chartData: [],  
        layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
        firstTabIcon,
        docLogo,
        selectedModelString: "",
        selectedModelTwoString: "", 
        selectedVariable : "", 
        datasetColumns: [] as string[], 
        selectedVariable:"",
        modelMetrics: {},
    };
},
computed:{
    isVariableSelectEnabled() {
        return this.selectedModelString !== "" && this.selectedModelTwoString !== "";
    },
    tableData() {
        if (!this.modelMetrics || !this.modelMetrics.models) {
        return []; // Return an empty array if the data is not (yet) available
            }


        const modelsArray = Object.keys(this.modelMetrics.models).map(modelKey => {
        const modelMetrics = this.modelMetrics.models[modelKey];
        console.log("Model Metrics", modelMetrics);
        return {
            model: modelKey, // This will be "Model_1", "Model_2", etc.
            AIC: modelMetrics.AIC,
            BIC: modelMetrics.BIC,
            Deviance: modelMetrics.Deviance
        };
    });

return modelsArray;
    

},
tableColumns() {
    return [
        { name: 'model', label: 'Model', field: 'model', align: 'left' },
        { name: 'AIC', label: 'AIC', field: 'AIC', align: 'left' },
        { name: 'BIC', label: 'BIC', field: 'BIC', align: 'left' },
        { name: 'Deviance', label: 'Deviance', field: 'Deviance', align: 'left' },
    ];
}
},
watch: {    
},
methods: {
    closeSideDrawer() {
        if (this.layoutRef) {
            this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
        }
    },
    async updateVariableString(value: string) {
        this.selectedVariable = value;
        const payload = {
        model1: this.selectedModelString,
        model2: this.selectedModelTwoString,

        }
        const dataResponse = await API.getModelComparisonData(payload);
        this.chartData = dataResponse?.data;
        console.log("Model Comaprison data:", this.chartData );
        const ModelMetricsResponse = await API.getModelMetrics(payload);
        this.modelMetrics = ModelMetricsResponse?.data;

        console.log("Model Metricc data:", this.modelMetrics);

    },
    async updateModelString(value: string) {
        this.selectedModelString = value;
    },
    async updateModelTwoString(value: string) {
        this.selectedModelTwoString = value;
    },
    async getDatasetColumns() {
    try {
    const response = await API.getDatasetColumns();
    console.log("Datasets:", response.data);
    this.datasetColumns = response.data;
    console.log("First assignment:", this.datasetColumns);
    } catch (error) {
        console.error('Error fetching datasets:', error);
        this.datasetColumns = [];
    }
}, 
},

mounted() {
    API.getModels().then((data: any) => {
    this.models = data.data;
    this.modelsString = this.models.map(item => item.name);
    
    });
    this.getDatasetColumns(); 
    this.ComparisonChartTitle = "Model Metrics";
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
.tab-content {
padding-left: 0px;
padding-right: 0px;
padding-top: 20px;
display: flex;
align-items: center;
gap: var(--bs-spacing-13, 52px);
min-height: 350px;
}
</style>



