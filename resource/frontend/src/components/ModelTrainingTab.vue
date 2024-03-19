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
                    <VariableSelect
                        label="Select a dataset"
                        :modelValue="selectedDatasetString"
                        :options="datasetsString"
                        @update:modelValue="updateDatasetString"
                        helpMessage="Charts will be generated based on this dataset"
                        style="min-width: 250px">
                    </VariableSelect>
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
                    <EmptyState
                        class="tab-content"
                        title="Model Training Parameters"
                        subtitle="Select training dataset in the left column to get started"
                        v-if="selectedDatasetString.length==0"/>
                    <div class="tab-content" v-else>
                    </div>
                    <div class="tab-content" v-else>
                        <!-- Conditionally render the Variables title only if datasetColumns has items -->
                        <q-card-section>
                            <h5 v-if="datasetColumns.length > 0">Algorithm Parameters </h5>
                        </q-card-section>
                        <q-card class="q-pa-sm">
                            <div class="form-group">
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
                        </q-card>
                        <q-card-section>
                            <h5 v-if="datasetColumns.length > 0">Feature Handling</h5>
                        </q-card-section>
                        <q-card class="q-pa-md">
                            <div v-for="(column, index) in datasetColumns" :key="index" class="column-management">
                                    <span class="column-name">{{ column.name }}</span>
                                    <VariableSelect
                                        label="Include/Exclude"
                                        :modelValue="column.isIncluded"
                                        :options="includeOptions"
                                        @update:modelValue="newValue => updateColumnProperty(index, 'isIncluded', newValue)"
                                        helpMessage="Include or exclude column for modelling"
                                        style="min-width: 150px">
                                    </VariableSelect>
                                    <!-- Replace q-btn-toggle for role -->
                                    <VariableSelect
                                        label="Column Role"
                                        :modelValue="column.role"
                                        :options="roleOptions"
                                        @update:modelValue="newValue => updateColumnProperty(index, 'role', newValue)"
                                        helpMessage="What role will the column play in modelling"
                                        style="min-width: 150px">
                                    </VariableSelect>
                                    <VariableSelect
                                        label="Column Type"
                                        :modelValue="column.type"
                                        :options="typeOptions"
                                        @update:modelValue="newValue => updateColumnProperty(index, 'type', newValue)"
                                        helpMessage="Does the column contain categorical or numerical data?"
                                        style="min-width: 150px">
                                    </VariableSelect>
                                    <VariableSelect
                                        label="Preprocessing"
                                        :modelValue="column.preprocessing"
                                        :options="preprocessingOptions"
                                        @update:modelValue="newValue => updatePreprocessing(index, newValue)"
                                        helpMessage="Preprocessing Method"
                                        style="min-width: 150px">
                                    </VariableSelect>
                            </div>
                        </q-card>
                        <q-btn color="primary" class="q-mt-md" label="Train Model" @click="submitVariables"></q-btn>
                    </div>
                </BsContent>
                
            </BsTab>
        
        </template>

        <script lang="ts">
        import { defineComponent } from "vue";
        import VariableSelect from './VariableSelect.vue';
        import EmptyState from './EmptyState.vue';
        import { BsTab, BsTabIcon, BsHeader, BsButton, BsDrawer, BsContent, BsTooltip } from "quasar-ui-bs";
        import docLogo from "../assets/images/doc-logo-example.svg";
        import firstTabIcon from "../assets/images/first-tab-icon.svg";
        import { API } from '../Api';

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
                BsTooltip
            },
            props: [],
            data() {
                return {            
                    selectedDatasetString: "",
                    selectedDistributionFunctionString: "",
                    selectedLinkFunctionString:"",
                    datasetsString: [],
                    chartData: [], 
                    layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
                    firstTabIcon,
                    docLogo,
                    includeOptions: [
                        {label: 'Include', value: true}, 
                        {label: 'Exclude', value: false}
                    ],
                    distributionOptions: [
                        { label: 'Gaussian', value: 'Gaussian' },
                        { label: 'Poisson', value: 'Poisson' },
                        { label: 'Tweedie', value: 'Tweedie' },
                    ],
                    linkOptions: [
                        { label: 'Log', value: 'Log' },
                        { label: 'Power', value: 'Power' },
                    ],
                    typeOptions: [
                        { label: 'Categorical', value: 'categorical' },
                        { label: 'Numerical', value: 'numerical' },
                    ],
                    preprocessingOptions: [
                        { label: 'Dummy Encode', value: 'DUMMIFY' },
                        { label: 'Drop One Dummy', value: 'DROP_ONE' },
                        { label: 'Normal Numerical', value: 'REGULAR' },
                    ],
                    roleOptions: [
                        {label: 'Exposure', value: 'Exposure'},
                        {label: 'Target', value: 'Target'},
                        {label: 'Variable', value: 'Variable'},
                    ],
                    datasetColumns: [], // Populate this based on your actual data
                };
            },
            methods: {
                closeSideDrawer() {
                    if (this.layoutRef) {
                        this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
                    }
                },
                updateModelProperty(property, value){
                    this[property]=value;
                    localStorage.setItem(property, value);
                    console.log(`updateModelProperty: Updating ${property} to ${value}`);
                },
                updatePreprocessing(index, newValue) {
                    const column = this.datasetColumns[index];
                    if (column) {
                        column.preprocessing = newValue;
                        // Since Vue 2 doesn't reactively update arrays on index, force update
                        this.$set(this.datasetColumns, index, column);
                    }
                },
                updateColumnProperty(columnIndex, property, value) {
                    const column = this.datasetColumns[columnIndex];
                    if (column) {
                            column[property] = value;
                        }
                        // Trigger a Vue reactivity update
                        this.datasetColumns.splice(columnIndex, 1, column);
                    },
                async updateDatasetString(value: string) {
                    this.selectedDatasetString = value;
                    localStorage.setItem('selectedDataset', value);
                    try {
                        const columnNames = await API.getDatasetColumns(value);
                        // Transform each column name into an object with additional properties
                        this.datasetColumns = columnNames.map(columnName => ({
                            name: columnName, 
                            isIncluded: {label: 'Include', value: true},
                            role: {label: 'Variable', value: 'Variable'}, 
                            type: { label: 'Categorical', value: 'categorical' },
                            preprocessing: { label: 'Dummy Encode', value: 'DUMMIFY' },
                        }));
                    } catch (error) {
                        console.error('Error fetching dataset columns:', error);
                        this.datasetColumns = [];
                    }
                    this.$emit('update:modelValue', value);
                },
                async fetchDatasets() {
                try {
                    const response = await API.getProjectDatasets();
                    this.datasetsString = response.data; // Assuming this is a data property for storing dataset names
                } catch (error) {
                    console.error('Error fetching datasets:', error);
                }
                },
                async submitVariables() {
                    // Define modelParameters outside of the reduce call to ensure it's accessible later
                    const modelParameters = {
                        distribution_function: this.selectedDistributionFunctionString.value,
                        link_function: this.selectedLinkFunctionString.value,
                    };

                    // Reduce function to construct Variables object    
                    const variableParameters = this.datasetColumns.reduce((acc, column) => {
                        const {name, isIncluded, role, type, preprocessing } = column;

                        acc[name] = {
                            role: role.value,
                            type: type.value,
                            processing: preprocessing.value, 
                            included: isIncluded.value
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

                async getDatasetColumns(value) {
                    try {
                    const columns = await API.getDatasetColumns(value);
                    console.log("Datasets:", columns);
                    this.datasetColumns = columns.map(columnName => ({
                        name: columnName,
                        isIncluded: false,
                        role: false,
                        type: 'Categorical',
                        preprocessing: 'Dummy Encode'
                    }));// Assuming this is a data property for storing dataset names
                    } catch (error) {
                        console.error('Error fetching datasets:', error);
                        this.datasetColumns = [];
                    }
                },  
            },
            mounted() {
                this.fetchDatasets(); 
                this.layoutRef = this.$refs.layout as InstanceType<typeof BsLayoutDefault>;
                const savedDistributionFunction = localStorage.getItem('DistributionFunction');
                const savedLinkFunction = localStorage.getItem('linkFunction');

            },
            emits: ['update:modelValue']
        })
        </script>
    <style scoped>
    .column-management {
            display: flex;
            align-items: center; /* Align items vertically */
            gap: 10px; /* Spacing between each item */
        }
    .column-name {
            font-weight: bold; /* Make the variable name stand out */
            margin-right: 10px; /* Ensure there's spacing after the name */
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

    </style>


