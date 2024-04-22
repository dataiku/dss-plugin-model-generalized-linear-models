<template>
              <EmptyState
                    class="tab-content"
                    title="One-Way Variable"
                    subtitle="Select variable in the left column to create chart"
                    v-if="chartData.length==0"/>
                <div class="tab-content" v-else>
                    <BarChart
                      v-if="selectedVariable"
                      :xaxisLabels="chartData.map(item => ((selectedVariable.variableType == 'categorical') ? item.Category : Number(item.Category)))"
                      :xaxisType="selectedVariable.variableType"
                      :barData="chartData.map(item => item.Value)"
                      :observedAverageLine="chartData.map(item => item.observedAverage)"
                      :fittedAverageLine="chartData.map(item => item.fittedAverage)"
                      :baseLevelPredictionLine="chartData.map(item => item.baseLevelPrediction)"
                      :chartTitle="selectedVariable.variable"
                      />
                    <BsTable v-if="selectedVariable.isInModel"
                      :title="selectedVariable.variable"
                      :rows="relativities"
                      :columns="relativitiesColumns"
                      :globalSearch="false"
                      row-key="name"
                    />
                </div>
    </template>

<script lang="ts">
import BarChart from './BarChart.vue'
import DocumentationContent from './DocumentationContent.vue'
import EmptyState from './EmptyState.vue';
import * as echarts from "echarts";
import type { DataPoint, ModelPoint, RelativityPoint, VariablePoint } from '../models';
import { defineComponent } from "vue";
import { API } from '../Api';
import { useLoader } from "../composables/use-loader";
import { BsButton, BsLayoutDefault, BsTable, BsCheckbox, BsSlider } from "quasar-ui-bs";
import type { QTableColumn } from 'quasar';

const columns: QTableColumn[] = [
        { name: 'class', align: 'center', label: 'Class', field: 'class',sortable: true},
        { name: 'relativity', align: 'center', label: 'Relativity', field: 'relativity', sortable: true},
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
    props: {
      reloadModels: {
        type: Boolean,
        default: false
      }
    },
    components: {
        BarChart,
        DocumentationContent,
        BsButton,
        BsLayoutDefault,
        EmptyState,
        BsTable,
        BsCheckbox,
        BsSlider,
    },
    data() {
        return {
            chartData: [] as DataPoint[],
            allData: [] as DataPoint[],
            relativitiesData: [] as RelativityPoint[],
            relativitiesTable: [] as RelativityPoint[],
            models: [] as ModelPoint[],
            modelsString: [] as string[],
            selectedModelString: "",
            layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
            variablePoints: [] as VariablePoint[],
            allVariables: [] as String[],
            variables: [] as VariablePoint[],
            selectedVariable: {} as VariablePoint,
            relativities: rows,
            relativitiesColumns: columns,
            inModelOnly: true,
            includeSuspectVariables: true,
            loading: false,
        };
    },
    watch: {
      reloadModels: {
          handler() {
            API.getModels().then((data: any) => {
              this.models = data.data;
              this.modelsString = this.models.map(item => item.name);
            });
          },
      },
      loading(newVal) {
          if (newVal) {
              useLoader("Loading data..").show();
          } else {
              useLoader().hide();
          }
      },
      selectedVariable(newValue: VariablePoint) {
        this.chartData = this.allData.filter(item => item.definingVariable === newValue.variable);
        this.relativitiesTable = this.relativitiesData.filter(item => item.variable === newValue.variable);
        this.relativitiesColumns = columns;
        this.relativities = this.relativitiesTable.map( (point) => {
          const relativity = {'class': point.category, 'relativity': Math.round(point.relativity*1000)/1000};
          return relativity
        })
      },
      allData(newValue: DataPoint[]) {
        this.chartData = this.allData.filter(item => item.definingVariable === this.selectedVariable.variable);
      }
    },
    methods: {
      closeSideDrawer() {
            if(this.layoutRef){
                this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
            }
        },
        async updateVariable(value: VariablePoint) {
          this.selectedVariable = value;
        },
        async updateModelString(value: string) {
          this.loading = true;
          this.selectedVariable = {} as VariablePoint;
          const model = this.models.filter( (v: ModelPoint) => v.name==value)[0];
          const variableResponse = await API.getVariables(model);
          this.variablePoints = variableResponse?.data;
          this.allVariables = this.variablePoints.map(item => item.variable);
          const dataResponse = await API.getData(model);
          this.allData = dataResponse?.data;
          const relativityResponse = await API.getRelativities(model);
          this.relativitiesData = relativityResponse?.data;
          this.selectedModelString = value;
          this.loading = false;
        },
        onClick: function() {
          API.exportModel().then(response => {
              const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', this.selectedModelString + '.csv'); // Set the filename for the download
              document.body.appendChild(link);
              link.click();
              window.URL.revokeObjectURL(url); // Clean up
          }).catch(error => {
              console.error('Error exporting model:', error);
          });
        },
    },
    mounted() {
      API.getModels().then((data: any) => {
        this.models = data.data;
        this.modelsString = this.models.map(item => item.name);
      });
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

.variable-select-container {
    padding: 20px;
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

.logo {
  display: block;
  margin: 0 auto 2rem;
}

.bs-btn {
  margin-top: 12px;
}

.button-container {
  margin-top: 12px
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