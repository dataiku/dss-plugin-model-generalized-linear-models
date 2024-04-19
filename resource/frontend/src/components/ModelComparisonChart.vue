<template>
    <v-chart
      :option="chartOption"
      ref="chart"
      autoresize
      :init-options="{
          renderer: 'canvas',
      }"
      style="height: 400px; width: 100%; min-width: 500px; min-width: 500px; min-height: 500px"
    />
  </template>
  
  <script lang="ts">
  import VChart from "vue-echarts";
  import { CanvasRenderer } from "echarts/renderers";
  import { use } from "echarts/core";
  
  use(CanvasRenderer);
  
  export default {
  name: 'ModifiedBarChart', // Changed the name to reflect the new functionality
  components: { VChart },
  props: {
    variableValues: {
      type: Array,
      required: true
    },
    model1ClaimFrequency: {
      type: Array,
      required: true
    },
    model2ClaimFrequency: {
      type: Array,
      required: true
    },
    exposures: {
      type: Array,
      required: true
    },
    observedAverage: {
      type: Array,
      required: true
    },
    chartTitle:{
        type: String,
        required: true,
        default: ''
      }
  },
  data() {
    return {
      chartOption: undefined as undefined | any,
    }
  },
  methods: {
        createChartData() {
        this.chartOption = {
            xAxis: {
                type: "category",
                data: this.variableValues,
                name: 'Variable Values',
                position: 'bottom', 
                nameLocation: 'center',
                nameGap: 50,
            },    
            yAxis: [
                    {
                        type: "value",
                        name: 'Claim Frequency',
                        nameLocation: 'center',
                        nameGap: 30,
                        position: 'left',
                    },
                {
                    type: "value",
                    name: 'Exposure',
                    nameLocation: 'center',
                    nameGap: 30,
                    position: 'right', // Use the right side for the exposure axis
                }   
                ],


            series: [
                {
                    name: "Model 1",
                    type: "line",
                    data: this.model1ClaimFrequency,
                    itemStyle: {
                        color: "#A77BCA",
                    },
                },
                {
                    name: "Model 2",
                    type: "line",
                    data: this.model2ClaimFrequency,
                    itemStyle: {
                        color: "#008675",
                    },
                    
                },
                {
                    name: "Observed Average",
                    type: "line",
                    data: this.observedAverage,
                    itemStyle: {
                        color: "#FFD700",
                    },
                    
                },
                {
                    name: "Exposure",
                    type: "bar",
                    yAxisIndex: 1, // This tells ECharts to use the second y-axis for this series
                    data: this.exposures,
                    itemStyle: {
                        color: "#D9D8D6", // Choose a color that stands out but harmonizes with the chart
                    },
                    showInLegend: false
                },
                // Optionally, represent Exposure by bar size or color here
            ],
            legend: {
                orient: 'horizontal',
                right: 0,
                top:30,

            },
            title: {
                text: this.chartTitle,
                left: 'center'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                },
                // Adapted tooltip to include Exposure information if necessary
            }
        };
    },
  },
  mounted() {
    this.createChartData();
    },
    watch: {
        variableValues: {
            deep: true,
            handler() {
                this.createChartData();
            },
        },
        },
}
  </script>
  