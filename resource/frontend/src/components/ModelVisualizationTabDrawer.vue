<template>
<div class="variable-select-container">
                <BsLabel
                    label="Select a model"
                    info-text="Charts will be generated with respect to this model">
                </BsLabel>
                <BsSelect
                    :modelValue="store.selectedModelString"
                    :all-options="store.modelsString"
                    @update:modelValue="updateModelString"
                    >
                </BsSelect>
                <div v-if="store.selectedModelString" class="button-container">
                <BsButton
                    class="bs-primary-button" 
                    unelevated
                    dense
                    no-caps
                    padding="4"
                    @click="onClick">Export Full Model</BsButton>
                </div>
                <BsCheckbox v-if="store.selectedModelString && tab=='one-way-variable'" v-model="store.includeSuspectVariables" label="Include Suspect Variables">
                </BsCheckbox>
                <BsLabel v-if="store.selectedModelString && tab=='one-way-variable'"
                    label="Select a Variable"
                    info-text="Charts will be generated with respect to this variable">
                </BsLabel>
                <BsSelect
                    v-if="store.selectedModelString && tab=='one-way-variable'"
                        v-model="selectedVariable"
                        :all-options="store.variablePoints"
                        @update:modelValue="updateVariable">
                        <template v-slot:selected-item="scope">
                        <q-item v-if="scope.opt">
                            {{ store.selectedVariable.variable }}
                        </q-item>
                    </template>
                            <template #option="props">
                                <q-item v-if="props.opt.isInModel || store.includeSuspectVariables" v-bind="props.itemProps" clickable>
                                    <q-item-section side>
                                    <div v-if="props.opt.isInModel">selected</div>
                                    <div v-else>unselected</div>
                                    </q-item-section>
                                <q-item-section class="bs-font-medium-2-normal">
                                    {{ props.opt.variable }}
                                </q-item-section>
                                </q-item>
                        </template>
                    </BsSelect>
                    <BsCheckbox v-model="store.rescale" 
                    v-if="store.selectedModelString && tab=='one-way-variable'"
                    @update:modelValue="updateRescale" 
                    label="Rescale?"></BsCheckbox>
                    <BsLabel v-if="store.selectedModelString && tab=='lift-chart'"
                    label="Select the number of bins">
                </BsLabel>
                <BsSlider v-if="store.selectedModelString && tab=='lift-chart'" @update:modelValue="updateNbBins" v-model="store.nbBins" :min="2" :max="20"/>
                    <BsLabel v-if="store.selectedModelString && (tab=='one-way-variable' || tab=='lift-chart')"
                    label="Run Analysis on">
                    </BsLabel>
                    <BsToggle v-if="store.selectedModelString && (tab=='one-way-variable' || tab=='lift-chart')" 
                    v-model="store.trainTest"
                    @update:modelValue="updateTrainTest"
                    labelRight="Test" 
                    labelLeft="Train"/>
                    <div v-if="store.selectedVariable.variable && tab=='one-way-variable'" class="button-container">
                    <BsButton class="bs-primary-button" 
                    unelevated
                    dense
                    no-caps
                    padding="4"
                    @click="onClickOneWay">Export One-Way Data</BsButton>
                    </div>
                    <div v-if="store.selectedModelString && tab=='variable-level-stats'" class="button-container">
                    <BsButton class="bs-primary-button" 
                    unelevated
                    dense
                    no-caps
                    padding="4"
                    @click="onClickStats">Export</BsButton>
                    </div>
                    <BsLabel v-if="store.selectedModelString && tab=='one-way-variable'"
                        label="Compare with model"
                        info-text="Second model to compare with the first one">
                    </BsLabel>
                    <BsSelect v-if="store.selectedModelString && tab=='one-way-variable'"
                        :modelValue="store.selectedModelString2"
                        :all-options="store.modelsString"
                        @update:modelValue="updateModelString2"
                        >
                    </BsSelect>
                </div>
</template>

<script lang="ts">
    import BarChart from './BarChart.vue'
    import DocumentationContent from './DocumentationContent.vue'
    import EmptyState from './EmptyState.vue';
    import OneWayTabContent from './OneWayTabContent.vue'
    import VariableLevelStatsTabContent from './VariableLevelStatsTabContent.vue'
    import LiftChartTabContent from './LiftChartTabContent.vue'
    import * as echarts from "echarts";
    import type { DataPoint, ModelPoint, RelativityPoint, VariablePoint, VariableLevelStatsPoint, LiftDataPoint, ModelMetrics, ModelMetricsDataPoint, BaseValue } from '../models';
    import { isErrorPoint } from '../models';
    import { defineComponent } from "vue";
    import { API } from '../Api';
    import { useLoader } from "../composables/use-loader";
    import { useNotification } from "../composables/use-notification";
    import { BsButton, BsLayoutDefault, BsTable, BsCheckbox, BsSlider, BsToggle } from "quasar-ui-bs";
    import docLogo from "../assets/images/doc-logo-example.svg";
    import oneWayIcon from "../assets/images/one-way.svg";
    import { useModelStore } from "../stores/webapp";
    
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
            BsToggle,
            OneWayTabContent,
            VariableLevelStatsTabContent,
            LiftChartTabContent
        },
        data() {
            return {
                store: useModelStore(),
                layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
                docLogo,
                oneWayIcon,
                tab: "one-way-variable",
                comparisonChartTitle: "Model Metrics",
                selectedVariable: {} as VariablePoint,
            };
        },
        watch: {
          reloadModels: {
              handler() {
                this.store.loadModels();
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
            this.store.selectedVariable = newValue;
            this.store.updateChartData();
          },
          allData(newValue: DataPoint[]) {
            this.store.allData = newValue;
            this.store.updateChartData();
          }
        },
        methods: {
            
            async updateVariable(value: VariablePoint) {
              this.store.selectedVariable = value;
            },
            async updateTrainTest(value: boolean) {
              this.store.updateTrainTest(value);
            },
            async updateRescale(value: boolean) {
              this.store.rescale = value;
              this.store.updateChartData();
            },
            async updateModelString(value: string) {
              this.store.updateModelString(value);
            },
            async updateModelString2(value: string) {
              this.store.updateModelString2(value);
            },
            async updateNbBins(value: number) {
                this.store.updateNbBins(value);
            },
            onClick: function() {
              this.store.exportModel();
            },
            onClickOneWay: function() {
              this.store.exportOneWay();
            },
            onClickStats: function() {
                this.store.exportStats();
            },
            notifyError(msg: string) {
                useNotification("negative", msg);
            },
            handleError(msg: any) {
                this.store.loading = false;
                console.error(msg);
                this.notifyError(msg);
            },
        },
        mounted() {
          this.store.loadModels();
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
      align-items: flex-start;
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
    
    .q-pa-lg {
        padding: 0
    }

    .card-container {
      display: flex;
      gap: 20px; /* Adjust the gap value as needed */
    }

    .bs-card {
      max-width: 440px;
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