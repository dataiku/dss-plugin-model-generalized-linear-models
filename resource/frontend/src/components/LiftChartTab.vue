<template>
<BsTab
            name="Lift Chart"
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
              <div class="variable-select-container">
              <BsLabel
                  label="Select a model"
                  info-text="Charts will be generated with respect to this model">
              </BsLabel>
              <BsSelect
                  :modelValue="selectedModelString"
                  :all-options="modelsString"
                  @update:modelValue="updateModelString"
                  style="min-width: 250px">
              </BsSelect>
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
              <EmptyState
                    class="tab-content"
                    title="Lift Chart"
                    subtitle="Select model in the left column to create chart"
                    v-if="chartData.length==0"/>
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
            </BsContent>
        </BsTab>
    </template>

<script lang="ts">
import LiftChart from './LiftChart.vue'
import DocumentationContent from './DocumentationContent.vue'
import EmptyState from './EmptyState.vue';
import * as echarts from "echarts";
import type { LiftDataPoint, ModelPoint } from '../models';
import { defineComponent } from "vue";
import { API } from '../Api';
import { BsButton, BsLayoutDefault, BsTable, BsCheckbox, BsSlider } from "quasar-ui-bs";
import docLogo from "../assets/images/doc-logo-example.svg";
import firstTabIcon from "../assets/images/first-tab-icon.svg";


export default defineComponent({
    props: {
      reloadModels: {
        type: Boolean,
        default: false
      }
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
    },
    data() {
        return {
            chartData: [] as LiftDataPoint[],
            models: [] as ModelPoint[],
            selectedModel: {} as ModelPoint,
            modelsString: [] as string[],
            selectedModelString: "",
            layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
            docLogo,
            firstTabIcon,
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
    },
    methods: {
      closeSideDrawer() {
            if(this.layoutRef){
                this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
            }
        },
        async updateModelString(value: string) {
          this.selectedModelString = value;
          const model = this.models.filter( (v: ModelPoint) => v.name==value)[0];
          const dataResponse = await API.getLiftData(model);
          this.chartData = dataResponse?.data;
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
