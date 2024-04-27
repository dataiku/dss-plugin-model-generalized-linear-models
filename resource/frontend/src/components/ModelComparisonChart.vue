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
    Category: {
      type: Array,
      required: true
    },
    model_1_observedAverage: {
      type: Array,
      required: true
    },
    model_1_fittedAverage: {
      type: Array,
      required: true
    },
    model1_baseLevelPrediction: {
      type: Array,
      required: true
    },
    model_2_observedAverage: {
      type: Array,
      required: true
    },
    model_2_fittedAverage:{
      type: Array,
      required: true
    },
    exposure: {
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
                data: this.Category,
                name: 'Variable Values',
                position: 'bottom', 
                nameLocation: 'center',
                nameGap: 50,
            },    
            yAxis: [
                    {
                        type: "value",
                        name: 'Value',
                        nameLocation: 'center',
                        nameGap: 30,
                        position: 'left',
                    },
                {
                    type: "value",
                    name: '',
                }   
                ],


            series: [
            {
                name: "Mdl 1:Fitted Avg",
                type: "line",
                data: this.model_1_fittedAverage,
                itemStyle: {
                    color: "#00BFFF",
                },
            },
            {
                name: "Mdl 2:Fitted Avg",
                type: "line",
                data: this.model_2_fittedAverage,
                itemStyle: {
                    color: "#FF7F50",
                },
                
            },
            {
                name: "Mdl 1:Obs Avg",
                type: "line",
                data: this.model_1_observedAverage,
                itemStyle: {
                    color: "#32CD32",
                },
                
            },
            {
                name: "Mdl 2:Obs Avg",
                type: "line",
                data: this.model_2_observedAverage,
                itemStyle: {
                    color: "#FFD700",
                },
                
            },
                {
                    name: "Exposure",
                    type: "bar",
                    yAxisIndex: 1, // This tells ECharts to use the second y-axis for this series
                    data: this.exposure,
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
        Category: {
            deep: true,
            handler() {
                this.createChartData();
            },
        },
        },
}
  </script>
  