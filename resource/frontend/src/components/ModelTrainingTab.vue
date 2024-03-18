    <template>
        <BsTab
            name="Model Training"
            docTitle="GLM Analyzer"
            :docIcon="docLogo"
        >
            <BsTabIcon>
                <img :src="firstTabIcon" alt="Target Definition Icon" />
            </BsTabIcon>
            <BsHeader>
                <BsButton
                    v-if="!layoutRef?.drawerOpen"
                    flat
                    round
                    class="open-side-drawer-btn"
                    size="15px"
                    @click="closeSideDrawer"
                    icon="mdi-arrow-right"
                >
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
                    <h2 v-if="datasetColumns.length > 0">GLM Model Parameter</h2>
                    <select name="Distribution Function">
                        <option disabled value="" selected>Select Distribution Function</option>
                        <option value="dummy_encode">Gaussian</option>
                        <option value="drop_one_dummy">Poisson</option>
                        <option value="normal_numerical">Tweedie</option>
                    </select>
                    <select name="Link Function">
                        <option disabled value="" selected>Select Link Function</option>
                        <option value="dummy_encode">Log</option>
                        <option value="drop_one_dummy">Power</option>
                    </select>

                    <h2 v-if="datasetColumns.length > 0">Variables</h2>
                    <div v-for="(column, index) in datasetColumns" :key="index" class="column-management">
                        <span class="column-name">{{ column.name }}</span>
                        
                        <!-- Toggle for Include/Exclude -->
                        <input type="checkbox" v-model="column.isIncluded" :id="'include-' + index">
                        <label :for="'include-' + index">{{ column.isIncluded ? 'Included' : 'Excluded' }}</label>
                        
                        <!-- Toggle for Set as Exposure/Remove as Exposure -->
                        <input type="checkbox" v-model="column.isExposure" :id="'exposure-' + index">
                        <label :for="'exposure-' + index">{{ column.isExposure ? 'Exposure Set' : 'Exposure Not Set' }}</label>
                        
                        <!-- Type selection -->
                        <select v-model="column.type">
                            <option disabled value="">Select Type</option>
                            <option value="categorical">Categorical</option>
                            <option value="numerical">Numerical</option>
                        </select>
                        <!-- Preprocessing selection -->
                        <select v-model="column.preprocessing">
                            <option disabled value="">Select Preprocessing</option>
                            <option value="dummy_encode">Dummy Encode</option>
                            <option value="drop_one_dummy">Drop One Dummy</option>
                            <option value="normal_numerical">Normal Numerical</option>
                        </select>
                    </div>
                    <BsButton
                        flat    
                        round
                        class="submit-variables-btn"
                        size="15px"
                        @click="submitVariables"
                        icon="mdi-send">    
                        <BsTooltip>Submit Variables</BsTooltip>
                    </BsButton>
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
                datasetColumns: [],
                layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
                firstTabIcon,
                docLogo
                // Example: Initialize your local state here
            };
        },
        methods: {
            closeSideDrawer() {
                if (this.layoutRef) {
                    this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
                }
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
    </style>