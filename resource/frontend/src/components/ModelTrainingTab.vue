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
                    subtitle="Select dataset in the left column to get started"
                    v-if="selectedDatasetString.length==0"/>
                <div class="tab-content" v-else>
                </div>
                <div class="tab-content" v-else>
                    <!-- Conditionally render the Variables title only if datasetColumns has items -->
                    <q-card-section>
                        <h5 v-if="datasetColumns.length > 0">Algorithm Parameters </h5>
                    </q-card-section>
                    <q-card class="q-pa-lg  ">
                        <div class="form-group">
                            <q-row class="q-mb-md">
                                <q-col cols="12" sm="4" class="q-pr-md">
                                    <q-btn-dropdown color="primary" :label="selectedDistributionFunction || 'Select Distribution Function'" no-caps no-wrap>
                                        <q-list>
                                        <q-item clickable v-close-popup @click="updateDistributionFunction('Gaussian')">
                                            <q-item-section>Gaussian</q-item-section>
                                        </q-item>
                                        <q-item clickable v-close-popup @click="updateDistributionFunction('Poisson')">
                                            <q-item-section>Poisson</q-item-section>
                                        </q-item>
                                        <q-item clickable v-close-popup @click="updateDistributionFunction('Tweedie')">
                                            <q-item-section>Tweedie</q-item-section>
                                        </q-item>
                                        </q-list>
                                    </q-btn-dropdown>
                                </q-col>
                            </q-row>
                            <q-row class="q-mb-md">
                                <q-col cols="12" sm="4" class="q-pr-md">
                                    <q-btn-dropdown color="primary" :label="selectedLinkFunction || 'Select Link Function'" no-caps no-wrap>
                                        <q-list>
                                        <q-item clickable v-close-popup @click="updateLinkFunction('Gaussian')">
                                            <q-item-section>Log</q-item-section>
                                        </q-item>
                                        <q-item clickable v-close-popup @click="updateLinkFunction('Poisson')">
                                            <q-item-section>Power</q-item-section>
                                        </q-item>
                                        </q-list>
                                    </q-btn-dropdown>
                                </q-col>
                            </q-row>
                        </div>
                    </q-card>
                    <q-card-section>
                        <h5 v-if="datasetColumns.length > 0">Feature Handling</h5>
                    </q-card-section>
                    <q-card class="q-pa-md">
                        
                        <div v-for="(column, index) in datasetColumns" :key="index" class="column-management">
                                <span class="column-name">{{ column.name }}</span>
                                <q-btn-toggle
                                    v-model="column.isIncluded"
                                    push
                                    glossy
                                    toggle-color="primary"
                                    :options="[
                                    {label: 'Include', value: 'Included'},
                                    {label: 'Excluded', value: 'Excluded'},
                                    ]"
                                />
                                <q-btn-toggle
                                    v-model="column.isExposure"
                                    push
                                    glossy
                                    toggle-color="primary"
                                    :options="[
                                    {label: 'Exposure', value: 'Exposure'},
                                    {label: 'Normal', value: 'Not Exposure'},
                                    ]"
                                />
                                <q-btn-toggle
                                    v-model="column.type"
                                    push
                                    glossy
                                    toggle-color="primary"
                                    :options="[
                                    {label: 'Categorical', value: 'Categorical'},
                                    {label: 'Numerical', value: 'Numerical'},
                                    ]"
                                />
                                <!-- Preprocessing selection -->
                                <q-btn-dropdown color="primary" :label="column.preprocessing || 'Select Preprocessing'">
                                    <q-list>
                                        <q-item clickable v-close-popup @click="updatePreprocessing(column, 'dummy_encode')">
                                        <q-item-section>
                                            <q-item-label>Dummy Encode</q-item-label>
                                        </q-item-section>
                                        </q-item>

                                        <q-item clickable v-close-popup @click="updatePreprocessing(column, 'drop_one_dummy')">
                                        <q-item-section>
                                            <q-item-label>Drop One Dummy</q-item-label>
                                        </q-item-section>
                                        </q-item>

                                        <q-item clickable v-close-popup @click="updatePreprocessing(column, 'normal_numerical')">
                                        <q-item-section>
                                            <q-item-label>Normal Numerical</q-item-label>
                                        </q-item-section>
                                        </q-item>
                                    </q-list>
                                </q-btn-dropdown>
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
        props: ['layoutRef'],
        data() {
            return {            
                selectedDatasetString: "",
                datasetsString: [],
                chartData: [], 
                layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
                firstTabIcon,
                docLogo,
                distributionFunction: '',
                linkFunction: '',
                distributionOptions: [
                    { label: 'Gaussian', value: 'dummy_encode' },
                    { label: 'Poisson', value: 'drop_one_dummy' },
                    { label: 'Tweedie', value: 'normal_numerical' },
                ],
                linkOptions: [
                    { label: 'Log', value: 'dummy_encode' },
                    { label: 'Power', value: 'drop_one_dummy' },
                ],
                typeOptions: [
                    { label: 'Categorical', value: 'categorical' },
                    { label: 'Numerical', value: 'numerical' },
                ],
                preprocessingOptions: [
                    { label: 'Dummy Encode', value: 'dummy_encode' },
                    { label: 'Drop One Dummy', value: 'drop_one_dummy' },
                    { label: 'Normal Numerical', value: 'normal_numerical' },
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
            updatePreprocessing(column, preprocessingValue) {
            column.preprocessing = preprocessingValue;
            },
            updateDistributionFunction(distributionFunction) {
                this.distributionFunction = distributionFunction;
                localStorage.setItem('DistributionFunction', distributionFunction);
            },
            updateLinkFunction(linkFunction) {
                this.linkFunction = linkFunction;
                localStorage.setItem('linkFunction', linkFunction);
            },

            // Generalized method to update any property of a column
            updateColumnProperty(column, property, value) {
                column[property] = value;
            },
            async updateDatasetString(value: string) {
                this.selectedDatasetString = value;
                localStorage.setItem('selectedDataset', value);
                try {
                    const columnNames = await API.getDatasetColumns(value);
                    // Transform each column name into an object with additional properties
                    this.datasetColumns = columnNames.map(columnName => ({
                        name: columnName, // Original column name from the API
                        isIncluded: false, // Default value
                        isExposure: false, // Default value
                        type: '', // Default to an empty string or another appropriate default value
                        preprocessing: '', // Default to an empty string or another appropriate default value
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
                const payload = this.datasetColumns.reduce((acc, column) => {
                    // Ensure all properties exist as expected. TypeScript users might need to define a type for `column`.
                    const { name, isIncluded, isExposure, type, preprocessing } = column;
                    
                    acc[name] = {
                        role: isExposure ? 'exposure' : 'input',
                        type: type || 'unspecified', // Use 'unspecified' if no type is selected
                        processing: preprocessing ? this.mapProcessing(preprocessing) : 'NONE', // Use 'NONE' if no preprocessing is selected
                        included: isIncluded
                    };
                    return acc;
                }, {});

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
                    isExposure: false,
                    type: '', // 'categorical' or 'numerical'
                    preprocessing: '' // 'dummy_encode', 'drop_one_dummy', 'normal_numerical'
                }));// Assuming this is a data property for storing dataset names
                } catch (error) {
                    console.error('Error fetching datasets:', error);
                    this.datasetColumns = [];
                }
            },
            mapProcessing(preprocessingValue) {
                // Map the preprocessing dropdown values to the expected backend format
                const mapping = {
                    dummy_encode: 'DUMMIFY',
                    drop_one_dummy: 'DROP_ONE',
                    normal_numerical: 'REGULAR'
                };
                return mapping[preprocessingValue] || 'NONE'; // Default to 'NONE' if not mapped
            }
            
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
.bs-card {
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px; /* Adds space between sections */
    background-color: #f9f9f9; /* Light background color for distinction */
    width: 100%;
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


