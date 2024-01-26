<template>
    <v-chart
      :option="chartOption"
      ref="chart"
      autoresize
      :init-options="{
          renderer: 'canvas',
      }"
      style="height: 400px; width: 100%; min-width: 500px"
    />
  </template>
  
<script lang="ts">
  import VChart from "vue-echarts";
  import { CanvasRenderer } from "echarts/renderers";
  import { use } from "echarts/core";

  use(CanvasRenderer);
  
  export default {
  name: 'BarChart',
  components: { VChart },
  props: {
    xaxisLabels: {
      type: Array,
      required: true
    },
    barData: {
      type: Array,
      required: true
    },
    observedAverageLine: {
      type: Array,
      required: true
    },
    fittedAverageLine: {
      type: Array,
      required: true
    },
    baseLevelPredictionLine: {
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
          xAxis: [{
              type: "category",
              data: this.xaxisLabels,
          }],
          yAxis: [
                    {
                        type: "value",
                        position: "left",
                        name: "value",
                        axisLine: { onZero: false, show: true },
                    },
                    {
                        type: "value",
                        position: "right",
                        name: "weights",
                        splitLine: {show: false} ,
                    },
                ],
                grid: {
                    top: 40,
                    left: 0,
                    right: 170,
                    containLabel: true,
                },
                series: [
                    {
                        name: "Weights",
                        type: "bar",
                        yAxisIndex: 1, // Assign to the right Y-axis
                        itemStyle: {
                            color: "#D9D8D6",
                            // color: "gray",
                            opacity: 0.7, // Semi-transparent or different color
                        },
                        z: 1, // Lower z-index for background
                        data: this.barData
                    },
                    {
                        name: "Observed Average",
                        type: "line",
                        yAxisIndex: 0, // Assign to the left Y-axis
                        itemStyle: {
                            color: "#A77BCA",

                            opacity: 0.7,
                        },
                        z: 3, // Higher z-index for main bars
                        data: this.observedAverageLine,
                    },
                    {
                        name: "Fitted Average",
                        type: "line",
                        yAxisIndex: 0, // Assign to the left Y-axis
                        itemStyle: {
                            color: "#008675",
                            opacity: 0.7,
                        },
                        z: 3, // Higher z-index for main bars
                        data: this.fittedAverageLine,
                    },
                    {
                        name: "Base Level Prediction",
                        type: "line",
                        yAxisIndex: 0, // Assign to the left Y-axis
                        itemStyle: {
                            color: "#26d07c",
                            opacity: 0.7,
                        },
                        z: 3, // Higher z-index for main bars
                        data: this.baseLevelPredictionLine,
                    },
                ],
                legend: {
                  // Try 'horizontal'
                  orient: 'vertical',
                  right: '0%',
                  top: 'center'
                },
                title: {
                  text: this.chartTitle,
                  left: 'center'
                }
            };
    },
  },
  mounted() {
      this.createChartData();
  },
  watch: {
    xaxisLabels: {
            deep: true,
            handler() {
                this.createChartData();
            },
        },
  },
}
</script>