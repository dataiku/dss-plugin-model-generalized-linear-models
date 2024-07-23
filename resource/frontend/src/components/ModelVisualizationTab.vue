<template>
    <BsTab
                name="Model Analysis"
                docTitle="GLM Analyzer"
                :docIcon="docLogo"
            >
                <BsTabIcon>
                    <img :src="oneWayIcon" alt="Target Definition Icon" />
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
                      >
                  </BsSelect>
                  <div v-if="selectedModelString" class="button-container">
                  <BsButton
                      class="bs-primary-button" 
                      unelevated
                      dense
                      no-caps
                      padding="4"
                      @click="onClick">Export Full Model</BsButton>
                    </div>
                  <BsCheckbox v-if="selectedModelString && tab=='one-way-variable'" v-model="includeSuspectVariables" label="Include Suspect Variables">
                  </BsCheckbox>
                  <BsLabel v-if="selectedModelString && tab=='one-way-variable'"
                      label="Select a Variable"
                      info-text="Charts will be generated with respect to this variable">
                   </BsLabel>
                    <BsSelect
                      v-if="selectedModelString && tab=='one-way-variable'"
                          v-model="selectedVariable"
                          :all-options="variablePoints"
                          @update:modelValue="updateVariable">
                          <template v-slot:selected-item="scope">
                            <q-item v-if="scope.opt">
                              {{ selectedVariable.variable }}
                            </q-item>
                        </template>
                              <template #option="props">
                                  <q-item v-if="props.opt.isInModel || includeSuspectVariables" v-bind="props.itemProps" clickable>
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
                      <BsCheckbox v-model="rescale" 
                      v-if="selectedVariable.isInModel && tab=='one-way-variable'"
                      @update:modelValue="updateRescale" 
                      label="Rescale?"></BsCheckbox>
                      <BsLabel v-if="selectedModelString && tab=='lift-chart'"
                        label="Select the number of bins">
                    </BsLabel>
                    <BsSlider v-if="selectedModelString && tab=='lift-chart'" @update:modelValue="updateNbBins" v-model="nbBins" :min="2" :max="20"/>
                      <BsLabel v-if="selectedModelString && (tab=='one-way-variable' || tab=='lift-chart')"
                        label="Run Analysis on">
                      </BsLabel>
                      <BsToggle v-if="selectedModelString && (tab=='one-way-variable' || tab=='lift-chart')" 
                      v-model="trainTest"
                      @update:modelValue="updateTrainTest"
                      labelRight="Test" 
                      labelLeft="Train"/>
                      <div v-if="selectedVariable.variable && tab=='one-way-variable'" class="button-container">
                        <BsButton class="bs-primary-button" 
                        unelevated
                        dense
                        no-caps
                        padding="4"
                        @click="onClickOneWay">Export One-Way Data</BsButton>
                      </div>
                      <div v-if="selectedModelString && tab=='variable-level-stats'" class="button-container">
                        <BsButton class="bs-primary-button" 
                        unelevated
                        dense
                        no-caps
                        padding="4"
                        @click="onClickStats">Export</BsButton>
                        </div>
                        <BsLabel v-if="selectedModelString && tab!='variable-level-stats'"
                          label="Compare with model"
                          info-text="Second model to compare with the first one">
                      </BsLabel>
                      <BsSelect v-if="selectedModelString && tab=='one-way-variable'"
                          :modelValue="selectedModelString2"
                          :all-options="modelsString"
                          @update:modelValue="updateModelString2"
                          >
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
                  <div class="card-container">
                    <BsCard v-if="selectedModelString" :title=selectedModelString style="width: 600px">
                        <template #content>
                            <BsCardColItems
                            :items=modelMetrics1
                            ></BsCardColItems>
                        </template>
                      </BsCard>
                      <BsCard v-if="selectedModelString2" :title=selectedModelString2 style="width: 600px">
                        <template #content>
                            <BsCardColItems
                            :items=modelMetrics2
                            ></BsCardColItems>
                        </template>
                      </BsCard>
                    </div>
                    <div class="tab-content">
                        <div class="q-pa-lg">
                            <q-tabs
                            v-model="tab"
                            dense
                            class="bs-underline-tabs bs-font-medium-3-normal bs-colored-text"
                            active-color="primary"
                            indicator-color="primary"
                            align="left"
                            no-caps
                            >
                            <q-tab name="one-way-variable" label="One-Way Variable" />
                            <q-tab name="variable-level-stats" label="Variable-Level Stats" />
                            <q-tab name="lift-chart" label="Lift Chart" />
                            </q-tabs>
                    
                    
                            <q-tab-panels v-model="tab" animated class="bs-colored-text">
                            <q-tab-panel name="one-way-variable">
                                <OneWayTabContent
                                :chart-data=chartData
                                :chart-data2=chartData2
                                :selected-variable=selectedVariable
                                :relativities=relativities
                                :relativities-columns=relativitiesColumns
                                ></OneWayTabContent>
                            </q-tab-panel>
                    
                            <q-tab-panel name="variable-level-stats">
                                <VariableLevelStatsTabContent
                                :variable-level-stats-data=variableLevelStatsData
                                :columns=variableLevelStatsColumns
                                ></VariableLevelStatsTabContent>
                            </q-tab-panel>
                    
                            <q-tab-panel name="lift-chart">
                                <LiftChartTabContent
                                :chart-data=liftChartData
                                ></LiftChartTabContent>
                            </q-tab-panel>
                            </q-tab-panels>
                        </div>
                    </div>
                </BsContent>
            </BsTab>
    </template>
    
    <script lang="ts">
    import BarChart from './BarChart.vue'
    import DocumentationContent from './DocumentationContent.vue'
    import EmptyState from './EmptyState.vue';
    import OneWayTabContent from './OneWayTabContent.vue'
    import VariableLevelStatsTabContent from './VariableLevelStatsTabContent.vue'
    import LiftChartTabContent from './LiftChartTabContent.vue'
    import * as echarts from "echarts";
    import type { DataPoint, ModelPoint, RelativityPoint, VariablePoint, VariableLevelStatsPoint, LiftDataPoint, ModelMetrics, ModelMetricsDataPoint } from '../models';
    import { isErrorPoint } from '../models';
    import { defineComponent } from "vue";
    import { API } from '../Api';
    import { useLoader } from "../composables/use-loader";
    import { useNotification } from "../composables/use-notification";
    import { BsButton, BsLayoutDefault, BsTable, BsCheckbox, BsSlider, BsToggle } from "quasar-ui-bs";
    import docLogo from "../assets/images/doc-logo-example.svg";
    import oneWayIcon from "../assets/images/one-way.svg";
    import type { QTableColumn } from 'quasar';

    function round_decimals(x : number) {
        return Math.round(x * 1000) / 1000
    }
    
    const columns: QTableColumn[] = [
            { name: 'class', align: 'center', label: 'Class', field: 'class',sortable: true},
            { name: 'relativity', align: 'center', label: 'Relativity', field: 'relativity', sortable: true},
          ]
    
    const variableLevelStatsColumns: QTableColumn[] = [
        { name: 'variable', align: 'center', label: 'Variable', field: 'variable',sortable: true},
        { name: 'value', align: 'center', label: 'Value', field: 'value',sortable: true},
        { name: 'coefficient', align: 'center', label: 'Coefficient', field: 'coefficient',sortable: true},
        { name: 'standard_error', align: 'center', label: 'Standard Error', field: 'standard_error',sortable: true},
        { name: 'standard_error_pct', align: 'center', label: 'Standard Error PCT', field: 'standard_error_pct',sortable: true},
        { name: 'weight', align: 'center', label: 'Weight', field: 'weight',sortable: true},
        { name: 'weight_pct', align: 'center', label: 'Weight PCT', field: 'weight_pct',sortable: true},
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
    
    const tableColumns: QTableColumn[] = [
        { name: 'model', align: 'left', label: 'Model', field: 'model', sortable: true },
        { name: 'AIC', align: 'left', label: 'AIC', field: 'AIC', sortable: true },
        { name: 'BIC', align: 'left', label: 'BIC', field: 'BIC', sortable: true },
        { name: 'Deviance', align: 'left', label: 'Deviance', field: 'Deviance', sortable: true },
    ];
    
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
                chartData: [] as DataPoint[],
                chartData2: [] as DataPoint[],
                liftChartData: [] as LiftDataPoint[],
                allData: [] as DataPoint[],
                relativitiesData: [] as RelativityPoint[],
                relativitiesTable: [] as RelativityPoint[],
                models: [] as ModelPoint[],
                selectedModel: {} as ModelPoint,
                modelsString: [] as string[],
                selectedModelString: "",
                selectedModelString2: "",
                layoutRef: undefined as undefined | InstanceType<typeof BsLayoutDefault>,
                docLogo,
                oneWayIcon,
                variablePoints: [] as VariablePoint[],
                allVariables: [] as String[],
                variables: [] as VariablePoint[],
                selectedVariable: {} as VariablePoint,
                relativities: rows,
                relativitiesColumns: columns,
                inModelOnly: true,
                includeSuspectVariables: true,
                loading: false,
                active_model:  {} as ModelPoint,
                trainTest: false,
                rescale: false,
                tab: "one-way-variable",
                variableLevelStatsData: [] as VariableLevelStatsPoint[],
                variableLevelStatsColumns: variableLevelStatsColumns,
                nbBins: 8 as number,
                comparisonChartTitle: "Model Metrics",
                tableColumns: tableColumns,
                modelMetrics1: {} as ModelMetricsDataPoint,
                comparedModel:  {} as ModelPoint,
                allData2: [] as DataPoint[],
                modelMetrics2: {} as ModelMetricsDataPoint,
                variableLevelStatsData2: [] as VariableLevelStatsPoint[],
                relativitiesData2: [] as RelativityPoint[],

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
            this.selectedVariable = newValue;
            this.updateChartData(this.selectedVariable, this.rescale, this.selectedModelString, this.selectedModelString);
          //   this.relativitiesTable = this.relativitiesData.filter(item => item.variable === newValue.variable);
          //   this.relativitiesColumns = columns;
          //   this.relativities = this.relativitiesTable.map( (point) => {
          //     const relativity = {'class': point.category, 'relativity': Math.round(point.relativity*1000)/1000};
          //     return relativity
          //   })
          //   if (this.rescale) {
          //       const baseCategory = this.relativitiesTable.find(item => item.relativity === 1);
          //       if (baseCategory) {
          //         const baseData = this.allData.find(item => item.Category === baseCategory.category && item.definingVariable === this.selectedVariable.variable);
          //         if (baseData) {
          //           const baseLevelPrediction = baseData.baseLevelPrediction;
          //           const fittedAverage = baseData.fittedAverage;
          //           const observedAverage = baseData.observedAverage;
          //       this.chartData = this.allData.filter(item => item.definingVariable === this.selectedVariable.variable).map(item => ({
          //           ...item,
          //           baseLevelPrediction: item.baseLevelPrediction / baseLevelPrediction,
          //           fittedAverage: item.fittedAverage / fittedAverage,
          //           observedAverage: item.observedAverage / observedAverage
          //           }));
          //         } else {
          //       this.chartData = this.allData.filter(item => item.definingVariable === newValue.variable);
          //       }
          //       if (this.selectedModelString2) {
          //         const baseData2 = this.allData2.find(item => item.Category === baseCategory.category && item.definingVariable === this.selectedVariable.variable);
          //         if (baseData2) {
          //           const baseLevelPrediction = baseData2.baseLevelPrediction;
          //           const fittedAverage = baseData2.fittedAverage;
          //           const observedAverage = baseData2.observedAverage;
          //       this.chartData2 = this.allData2.filter(item => item.definingVariable === this.selectedVariable.variable).map(item => ({
          //           ...item,
          //           baseLevelPrediction: item.baseLevelPrediction / baseLevelPrediction,
          //           fittedAverage: item.fittedAverage / fittedAverage,
          //           observedAverage: item.observedAverage / observedAverage
          //           }));
          //         } else {
          //       this.chartData2 = this.allData2.filter(item => item.definingVariable === newValue.variable);
          //       }
          //       }

          //     } else {
          //       this.chartData = this.allData.filter(item => item.definingVariable === newValue.variable);
          //       if (this.selectedModelString2) {
          //         this.chartData2 = this.allData2.filter(item => item.definingVariable === newValue.variable);
          //       }
          //     }
          //   } else {
          //       this.chartData = this.allData.filter(item => item.definingVariable === newValue.variable);
          //       if (this.selectedModelString2) {
          //         this.chartData2 = this.allData2.filter(item => item.definingVariable === newValue.variable);
          //       }
          // }
          },
          allData(newValue: DataPoint[]) {
            this.updateChartData(this.selectedVariable, this.rescale, this.selectedModelString, this.selectedModelString);
            //  this.chartData = this.allData.filter(item => item.definingVariable === this.selectedVariable.variable);
            //  if (this.rescale) {
            //     const baseCategory = this.relativitiesTable.find(item => item.relativity === 1);
            //     if (baseCategory) {
            //       const baseData = this.allData.find(item => item.Category === baseCategory.category && item.definingVariable === this.selectedVariable.variable);
            //       if (baseData) {
            //         const baseLevelPrediction = baseData.baseLevelPrediction;
            //         const fittedAverage = baseData.fittedAverage;
            //         const observedAverage = baseData.observedAverage;
            //     this.chartData = this.allData.filter(item => item.definingVariable === this.selectedVariable.variable).map(item => ({
            //         ...item,
            //         baseLevelPrediction: item.baseLevelPrediction / baseLevelPrediction,
            //         fittedAverage: item.fittedAverage / fittedAverage,
            //         observedAverage: item.observedAverage / observedAverage
            //       }));
            //       } else {
            //     this.chartData = this.allData.filter(item => item.definingVariable === this.selectedVariable.variable);
            //   }
            //     } else {
            //     this.chartData = this.allData.filter(item => item.definingVariable === this.selectedVariable.variable);
            //   }
            //   } else {
            //     this.chartData = this.allData.filter(item => item.definingVariable === this.selectedVariable.variable);
            //   }
          }
        },
        methods: {
          closeSideDrawer() {
                if(this.layoutRef){
                    this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
                }
            },
            async updateChartData(variable: VariablePoint, rescale: boolean, modelString1: string, modelString2: string | null) {
              this.relativitiesTable = this.relativitiesData.filter(item => item.variable === variable.variable);
            this.relativitiesColumns = columns;
            this.relativities = this.relativitiesTable.map( (point) => {
              const relativity = {'class': point.category, 'relativity': Math.round(point.relativity*1000)/1000};
              return relativity
            })
            if (rescale) {
                const baseCategory = this.relativitiesTable.find(item => item.relativity === 1);
                if (baseCategory) {
                  const baseData = this.allData.find(item => item.Category === baseCategory.category && item.definingVariable === this.selectedVariable.variable);
                  if (baseData) {
                    const baseLevelPrediction = baseData.baseLevelPrediction;
                    const fittedAverage = baseData.fittedAverage;
                    const observedAverage = baseData.observedAverage;
                this.chartData = this.allData.filter(item => item.definingVariable === this.selectedVariable.variable).map(item => ({
                    ...item,
                    baseLevelPrediction: item.baseLevelPrediction / baseLevelPrediction,
                    fittedAverage: item.fittedAverage / fittedAverage,
                    observedAverage: item.observedAverage / observedAverage
                    }));
                  } else {
                this.chartData = this.allData.filter(item => item.definingVariable === variable.variable);
                }
                if (modelString2) {
                  const baseData2 = this.allData2.find(item => item.Category === baseCategory.category && item.definingVariable === variable.variable);
                  if (baseData2) {
                    const baseLevelPrediction = baseData2.baseLevelPrediction;
                    const fittedAverage = baseData2.fittedAverage;
                    const observedAverage = baseData2.observedAverage;
                this.chartData2 = this.allData2.filter(item => item.definingVariable === variable.variable).map(item => ({
                    ...item,
                    baseLevelPrediction: item.baseLevelPrediction / baseLevelPrediction,
                    fittedAverage: item.fittedAverage / fittedAverage,
                    observedAverage: item.observedAverage / observedAverage
                    }));
                  } else {
                this.chartData2 = this.allData2.filter(item => item.definingVariable === variable.variable);
                }
                }

              } else {
                this.chartData = this.allData.filter(item => item.definingVariable === variable.variable);
                if (modelString2) {
                  this.chartData2 = this.allData2.filter(item => item.definingVariable === variable.variable);
                }
              }
            } else {
                this.chartData = this.allData.filter(item => item.definingVariable === variable.variable);
                if (modelString2) {
                  this.chartData2 = this.allData2.filter(item => item.definingVariable === variable.variable);
                }
          }
            },
            async updateVariable(value: VariablePoint) {
              this.selectedVariable = value;
            },
            async updateTrainTest(value: boolean) {
              this.trainTest = value;
              const modelTrainPoint = {id: this.active_model.id, name: this.active_model.name, trainTest: this.trainTest};
              const dataResponse = await API.getData(modelTrainPoint);
              this.allData = dataResponse?.data;
              const modelLiftPoint = { nbBins: this.nbBins, id: modelTrainPoint.id, name: modelTrainPoint.name, trainTest: this.trainTest};
              const liftDataResponse = await API.getLiftData(modelLiftPoint);
              this.liftChartData = liftDataResponse?.data;
            },
            async updateRescale(value: boolean) {
              this.rescale = value;
              this.updateChartData(this.selectedVariable, this.rescale, this.selectedModelString, this.selectedModelString);
            },
            async updateModelString(value: string) {
              this.loading = true;
              try {
                this.selectedVariable = {} as VariablePoint;
                const model = this.models.filter( (v: ModelPoint) => v.name==value)[0];
                this.active_model = model
                const variableResponse = await API.getVariables(model)
                if (isErrorPoint(variableResponse?.data)) {
                  this.handleError(variableResponse?.data.error);
                } else {
                  this.variablePoints = variableResponse?.data;
                  this.allVariables = this.variablePoints.map(item => item.variable);
                  const modelTrainPoint = {id: model.id, name: model.name, trainTest: this.trainTest};
                  const dataResponse = await API.getData(modelTrainPoint);
                  this.allData = dataResponse?.data;
                  const relativityResponse = await API.getRelativities(model);
                  this.relativitiesData = relativityResponse?.data;
                  this.selectedModelString = value;
                }
                const variableLevelStatsResponse = await API.getVariableLevelStats(model);
                this.variableLevelStatsData = variableLevelStatsResponse?.data.map( (point) => {
                    const variableLevelStats = {'variable': point.variable, 'value': point.value, 
                                                'coefficient': round_decimals(point.coefficient),
                                                'standard_error': round_decimals(point.standard_error), 
                                                'standard_error_pct': round_decimals(point.standard_error_pct),
                                                'weight': round_decimals(point.weight), 
                                                'weight_pct': round_decimals(point.weight_pct), 
                                                'relativity': round_decimals(point.relativity)};
                    return variableLevelStats
                });
                const modelNbBins = { nbBins: this.nbBins, id: model.id, name: model.name, trainTest: this.trainTest};
                const dataResponse = await API.getLiftData(modelNbBins);
                this.liftChartData = dataResponse?.data;
                const ModelMetricsResponse = await API.getModelMetrics(model);
                this.modelMetrics1 = ModelMetricsResponse?.data as ModelMetricsDataPoint;
            } catch (err) {
                this.handleError(err);
            } finally {
              this.loading = false;
            }
            },
            async updateModelString2(value: string) {
              this.loading = true;
              try {
                this.selectedVariable = {} as VariablePoint;
                const model = this.models.filter( (v: ModelPoint) => v.name==value)[0];
                this.comparedModel = model;
                const modelTrainPoint = {id: model.id, name: model.name, trainTest: this.trainTest};
                const dataResponse = await API.getData(modelTrainPoint);
                this.allData2 = dataResponse?.data;
                const relativityResponse = await API.getRelativities(model);
                this.relativitiesData2 = relativityResponse?.data;
                this.selectedModelString2 = value;
                const variableLevelStatsResponse = await API.getVariableLevelStats(model);
                this.variableLevelStatsData2 = variableLevelStatsResponse?.data.map( (point) => {
                    const variableLevelStats = {'variable': point.variable, 'value': point.value, 
                                                'coefficient': round_decimals(point.coefficient),
                                                'standard_error': round_decimals(point.standard_error), 
                                                'standard_error_pct': round_decimals(point.standard_error_pct),
                                                'weight': round_decimals(point.weight), 
                                                'weight_pct': round_decimals(point.weight_pct), 
                                                'relativity': round_decimals(point.relativity)};
                    return variableLevelStats
                });
                const ModelMetricsResponse = await API.getModelMetrics(model);
                this.modelMetrics2 = ModelMetricsResponse?.data as ModelMetricsDataPoint;
              } catch (err) {
                  this.handleError(err);
              } finally {
                this.loading = false;
              }
            },
            async updateNbBins(value: number) {
                this.loading = true;
                this.nbBins = value;
                const model = this.models.filter( (v: ModelPoint) => v.name==this.selectedModelString)[0];
                const modelNbBins = { nbBins: this.nbBins, id: model.id, name: model.name, trainTest: this.trainTest};
                const dataResponse = await API.getLiftData(modelNbBins);
                this.liftChartData = dataResponse?.data;
                this.loading = false;
            },
            onClick: function() {
              API.exportModel(this.active_model).then(response => {
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
            onClickOneWay: function() {
              API.exportOneWay({id: this.active_model.id, 
                name: this.active_model.name, 
                variable: this.selectedVariable.variable, 
                trainTest: this.trainTest,
                rescale: this.rescale}).then(response => {
                  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
                  const link = document.createElement('a');
                  link.href = url;
                  link.setAttribute('download', this.selectedModelString + '_' + this.selectedVariable.variable + '_' + (this.trainTest ? "test" : "train") + (this.rescale ? "_rescaled" : "") + '.csv'); // Set the filename for the download
                  document.body.appendChild(link);
                  link.click();
                  window.URL.revokeObjectURL(url); // Clean up
              }).catch(error => {
                  console.error('Error exporting model:', error);
              });
            },
            onClickStats: function() {
                API.exportVariableLevelStats(this.active_model).then(response => {
                    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'variable_level_stats.csv'); // Set the filename for the download
                    document.body.appendChild(link);
                    link.click();
                    window.URL.revokeObjectURL(url); // Clean up
                }).catch(error => {
                    console.error('Error exporting model:', error);
                });
            },
            notifyError(msg: string) {
                useNotification("negative", msg);
            },
            handleError(msg: any) {
                this.loading = false;
                console.error(msg);
                this.notifyError(msg);
            },
        },
        computed: {
            tableData() {
                if (!this.modelMetrics1) {
                return []; // Return an empty array if the data is not (yet) available
                    }
                const modelsArray = Object.keys([this.modelMetrics1]).map(modelKey => {
                const modelMetrics = this.modelMetrics1;
                console.log("Model Metrics", modelMetrics);
                return {
                    model: this.active_model.name, // This will be "Model_1", "Model_2", etc.
                    AIC: modelMetrics.AIC,
                    BIC: modelMetrics.BIC,
                    Deviance: modelMetrics.Deviance
                    };
                });

                return modelsArray;
            

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

function updateChartData(selectedVariable: any, rescale: any, selectedModelString: any, selectedModelString1: any) {
  throw new Error('Function not implemented.');
}

function updateChartData(selectedVariable: any, rescale: any, selectedModelString: any, selectedModelString1: any) {
  throw new Error('Function not implemented.');
}
    