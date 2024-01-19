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
                <!-- <Header
                    :target="store.draftTarget.target"
                    :target-date="store.draftTarget.targetDate"
                    :target-type="store.draftTarget.targetType"
                ></Header> -->
            </BsHeader>
            <BsDrawer>
              <div class="mb-3">
                <label for="variableSelect" class="form-label">Choose a Variable</label>
                <select class="form-select" id="variableSelect" v-model="selectedDefiningVariable">
                  <option disabled value="">Please select a variable</option>
                  <option v-for="variable in definingVariables" :key="variable" :value="variable">
                    {{ variable }}
                  </option>
                </select>
              </div>
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
                <div class="tab-content">
                    <BarChart
                        v-if="selectedDefiningVariable"
                        :xaxisLabels="chartData.map(item => item.Category)"
                        :barData="chartData.map(item => item.Value)"
                        :observedAverageLine="chartData.map(item => item.observedAverage)"
                        :fittedAverageLine="chartData.map(item => item.fittedAverage)"
                        :chartTitle="selectedDefiningVariable"
                      />
                </div>
            </BsContent>
        </BsTab>
        
    </BsLayoutDefault>
</template>

<script lang="ts">
import BarChart from './components/BarChart.vue'
import * as echarts from "echarts";
import type { DataPoint } from './models';
import { defineComponent } from "vue";
import { API } from './Api';
import { BsLayoutDefault } from "quasar-ui-bs";
import docLogo from "./assets/images/doc-logo-example.svg";
import firstTabIcon from "./assets/images/first-tab-icon.svg";

export default defineComponent({
    components: {
        BarChart
    },
    data() {
        return {
            chartData: [] as DataPoint[],
            selectedDefiningVariable: "",
            allData: [] as DataPoint[],
            layoutRef: undefined as undefined | typeof BsLayoutDefault,
            docLogo,
            firstTabIcon,
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
    methods: {
      closeSideDrawer() {
            if(this.layoutRef){
                this.layoutRef.drawerOpen = !this.layoutRef.drawerOpen;
            }
        },
    },
    mounted() {
      API.getData().then((data: any) => {
        this.allData = data.data;
      });
    }
})


</script>

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
