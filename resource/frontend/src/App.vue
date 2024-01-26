<template>
    <BsLayoutDefault ref="layout">
        <BsTab
            name="Variable Selection"
            docTitle="Process Analyzer"
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
                  :modelValue="selectedModel"
                  :options="models"
                  @update:modelValue="updateModel"
                  label="Select a model"
                  helpMessage="Charts will be generated with respect to this model"
                  style="min-width: 250px"></VariableSelect>
                <VariableSelect
                  v-if="selectedModel"
                  :modelValue="selectedDefiningVariable"
                  :options="definingVariables"
                  @update:modelValue="updateDefiningVariable"
                  label="Select a variable"
                  helpMessage="Charts will be generated with respect to this variable"
                  style="min-width: 250px"></VariableSelect>
                <BsButton
                    flat
                    round
                    class="close-side-drawer-btn"
                    size="15px"
                    @click="closeSideDrawer"
                    icon="mdi-arrow-left"
                >
                    <BsTooltip>Close sidebar</BsTooltip>
                </BsButton>
            </BsDrawer>
            <BsDocumentation>
                <DocumentationContent></DocumentationContent>
            </BsDocumentation>
            <BsContent>
              <EmptyState
                    class="tab-content"
                    title="One-Way Variable"
                    subtitle="Select variable in the left column to create chart"
                    v-if="chartData.length==0"/>
                <div class="tab-content" v-else>
                    <BarChart
                      v-if="selectedDefiningVariable"
                      :xaxisLabels="chartData.map(item => item.Category)"
                      :barData="chartData.map(item => item.Value)"
                      :observedAverageLine="chartData.map(item => item.observedAverage)"
                      :fittedAverageLine="chartData.map(item => item.fittedAverage)"
                      :baseLevelPredictionLine="chartData.map(item => item.baseLevelPrediction)"
                      :chartTitle="selectedDefiningVariable"
                      />
                    <BsTable
                      title="Relativities"
                      :rows="relativities"
                      :columns="relativitiesColumns"
                      row-key="name"
                    />
                </div>
            </BsContent>
        </BsTab>
        
    </BsLayoutDefault>
</template>

<script lang="ts">
import BarChart from './components/BarChart.vue'
import VariableSelect from './components/VariableSelect.vue'
import DocumentationContent from './components/DocumentationContent.vue'
import EmptyState from './components/EmptyState.vue';
import * as echarts from "echarts";
import type { DataPoint, ModelPoint } from './models';
import { defineComponent } from "vue";
import { API } from './Api';
import { BsButton, BsLayoutDefault, BsTable } from "quasar-ui-bs";
import docLogo from "./assets/images/doc-logo-example.svg";
import firstTabIcon from "./assets/images/first-tab-icon.svg";

const columns = [
        { name: 'class', align: 'center', label: 'Class', field: 'class', sortable: true, dataType:'string' },
        { name: 'relativity', align: 'center', label: 'Relativity', field: 'relativity', sortable: true, dataType:'double' },
      ]

const rows = [
    {
        class: 'January',
        relativity: 1.0,
    },
    {
        class: 'February',
        relativity: 1.087,
    },
    {
        class: 'March',
        relativity: 0.98,
    },
    {
        class: 'April',
        relativity: 1.12,
    }
  ]

export default defineComponent({
    components: {
        BarChart,
        VariableSelect,
        DocumentationContent,
        BsButton,
        BsLayoutDefault,
        EmptyState,
        BsTable
    },
    data() {
        return {
            chartData: [] as DataPoint[],
            selectedDefiningVariable: "",
            allData: [] as DataPoint[],
            models: [] as ModelPoint[],
            selectedModel: "",
            layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
            docLogo,
            firstTabIcon,
            definingVariables: [] as String[],
            relativities: rows,
            relativitiesColumns: columns,
        };
    },
    watch: {
      selectedDefiningVariable(newValue: string) {
        this.chartData = this.allData.filter(item => item.definingVariable === newValue);
      }
    },
    methods: {
      closeSideDrawer() {
            if(this.layoutRef){
                this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
            }
        },
        async updateDefiningVariable(value: string) {
          this.selectedDefiningVariable = value;
        },
        async updateModel(value: string) {
          this.selectedModel = value;
          const dataResponse = await API.getData({ id: value });
          console.log(dataResponse);
          console.log(dataResponse.data);
          console.log(dataResponse?.data);
          this.allData = dataResponse?.data;
          this.definingVariables = [...new Set(this.allData.map(item => item.definingVariable))];
        }
    },
    mounted() {
      // API.getData().then((data: any) => {
      //   this.allData = data.data;
      //   this.definingVariables = [...new Set(this.allData.map(item => item.definingVariable))];
      // });
      API.getModels().then((data: any) => {
        this.models = data.data;
      });
      this.layoutRef = this.$refs.layout as InstanceType<typeof BsLayoutDefault>;
    }
})
</script>

<style lang="scss" scoped>

:deep(.toggle-left-button) {
    display: none;
}

header {
  line-height: 1.5;
}

.tab-content {
  padding-left: 0px;
  padding-right: 100px;
  padding-top: 20px;
  display: flex;
  align-items: center;
  gap: var(--bs-spacing-13, 52px);
  min-height: 350px;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
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
</style>
