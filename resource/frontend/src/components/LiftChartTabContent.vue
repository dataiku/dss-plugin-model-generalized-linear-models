<template>
      <EmptyState
          class="tab-content"
          title="Lift Chart"
          subtitle="Select model in the left column to create chart"
          v-if="chartData.length == 0"/>
      <div class="tab-content" v-else>
          <LiftChart
              v-if="selectedModel"
              :xaxisLabels="chartData.map(item => item.Category)"
              :barData="chartData.map(item => item.Value)"
              :observedData="chartData.map(item => item.observedAverage)"
              :predictedData="chartData.map(item => item.fittedAverage)"
              chartTitle="Lift Chart"
          />
      </div>
</template>

<script lang="ts">
import LiftChart from './LiftChart.vue'
import DocumentationContent from './DocumentationContent.vue'
import EmptyState from './EmptyState.vue';
import { useLoader } from "../composables/use-loader";
import * as echarts from "echarts";
import type { LiftDataPoint, ModelPoint, ModelNbBins, DataPoint } from '../models';
import { defineComponent } from "vue";
import { API } from '../Api';
import { BsButton, BsLayoutDefault, BsTable, BsCheckbox, BsSlider, BsToggle } from "quasar-ui-bs";
import docLogo from "../assets/images/doc-logo-example.svg";
import liftChartIcon from "../assets/images/lift-chart.svg";


export default defineComponent({
    props: {
      reloadModels: {
        type: Boolean,
        default: false
      },
      chartData: {
        type: Array<DataPoint>,
        default: []
      },
    },
    components: {
        LiftChart,
        DocumentationContent,
        BsButton,
        BsLayoutDefault,
        EmptyState,
        BsTable,
        BsCheckbox,
        BsSlider,
        BsToggle
    },
    data() {
        return {
            models: [] as ModelPoint[],
            selectedModel: {} as ModelPoint,
            modelsString: [] as string[],
            selectedModelString: "",
            layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
            docLogo,
            liftChartIcon,
            loading: false,
            nbBins: 8,
            trainTest: false
        };
    },
        async updateModelString(value: string) {
          this.loading = true;
          this.selectedModelString = value;
          const model = this.models.filter( (v: ModelPoint) => v.name==value)[0];
          const modelNbBins = { nbBins: this.nbBins, id: model.id, name: model.name, trainTest: this.trainTest};
          const dataResponse = await API.getLiftData(modelNbBins);
          this.chartData = dataResponse?.data;
          this.loading = false;
        },
        async updateNbBins(value: number) {
          this.loading = true;
          this.nbBins = value;
          const model = this.models.filter( (v: ModelPoint) => v.name==this.selectedModelString)[0];
          const modelNbBins = { nbBins: this.nbBins, id: model.id, name: model.name, trainTest: this.trainTest};
          const dataResponse = await API.getLiftData(modelNbBins);
          this.chartData = dataResponse?.data;
          this.loading = false;
        },
        async updateTrainTest(value: boolean) {
          this.loading = true;
          this.trainTest = value;
          const model = this.models.filter( (v: ModelPoint) => v.name==this.selectedModelString)[0];
          const modelTrainPoint = { nbBins: this.nbBins, id: model.id, name: model.name, trainTest: this.trainTest};
          const dataResponse = await API.getLiftData(modelTrainPoint);
          this.chartData = dataResponse?.data;
          this.loading = false;
        }
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

.variable-select-container {
    padding: 20px;
}

</style>
