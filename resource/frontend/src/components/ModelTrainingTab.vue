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
                v-if="chartData.length==0"/>
            <div class="tab-content" v-else>
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
                const columns = await API.getDatasetColumns(value);
                this.datasetColumns = columns;
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
        async getDatasetColumns() {
            try {
            const response = await API.getDatasetColumns(value);
            this.columnNames = response.data; // Assuming this is a data property for storing dataset names
            } catch (error) {
                console.error('Error fetching datasets:', error);
            }
        }
        
    },
    mounted() {
        this.fetchDatasets(); 
        this.layoutRef = this.$refs.layout as InstanceType<typeof BsLayoutDefault>;

    },
    emits: ['update:modelValue']
})
</script>
