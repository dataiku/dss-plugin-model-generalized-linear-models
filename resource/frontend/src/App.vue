<script lang="ts">
import BarChart from './components/BarChart.vue'
import * as echarts from "echarts";
import type { DataPoint } from './models';
import { defineComponent } from "vue";
import { API } from './Api';

export default defineComponent({
    components: {
        BarChart
    },
    data() {
        return {
            chartData: [] as DataPoint[],
            //definingVariables: "",
            selectedDefiningVariable: "",
            allData: [] as DataPoint[],
        };
    },
    computed: {
      definingVariables() {
        if (this.allData) {
          return [...new Set(this.allData.map(item => item.definingVariable))];
        }
        return [];
      }
    },
    watch: {
      selectedDefiningVariable(newValue: string) {
        this.chartData = this.allData.filter(item => item.definingVariable === newValue);
      }
    },
    mounted() {
      API.getData().then((data: any) => {
        this.allData = data.data;
      });
    }
})


</script>

<template>
  <div class="container mt-3">
    <!-- Title with Bootstrap display class and margin bottom utility -->
    <h1 class="display-4 text-center mb-4">One Way Variable Analysis</h1>
    
    <!-- Dropdown with Bootstrap form-select class -->
    <div class="mb-3">
      <label for="variableSelect" class="form-label">Choose a Variable</label>
      <select class="form-select" id="variableSelect" v-model="selectedDefiningVariable">
        <option disabled value="">Please select a variable</option>
        <option v-for="variable in definingVariables" :key="variable" :value="variable">
          {{ variable }}
        </option>
      </select>
    </div>
    
    <!-- Chart container -->
    <div class="chart-container mb-3">
      <BarChart
        v-if="selectedDefiningVariable"
        :xaxisLabels="chartData.map(item => item.Category)"
        :barData="chartData.map(item => item.Value)"
        :observedAverageLine="chartData.map(item => item.observedAverage)"
        :fittedAverageLine="chartData.map(item => item.fittedAverage)"
        :chartTitle="selectedDefiningVariable"
      />
    </div>
  </div>
</template>

<style scoped>
header {
  line-height: 1.5;
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
</style>
