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
            </BsHeader>
            <BsDrawer>
              <!-- <BsSelect
                    v-model="selectedDefiningVariable"
                    :options="definingVariables"
                    clear-icon="clear"
                    use-input
                    clearable
                    input-debounce="0"
                /> -->
                <VariableSelect
                :selectedTarget="selectedDefiningVariable"
                :options="definingVariables"
                label="Select a variable"
                helpMessage="Charts will be created for the selected variable"
                style="min-width: 250px"
                />
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
import VariableSelect from './components/VariableSelect.vue'
import DocumentationContent from "./components/DocumentationContent.vue"
import * as echarts from "echarts";
import type { DataPoint } from './models';
import { defineComponent } from "vue";
import { API } from './Api';
import { BsButton, BsLayoutDefault } from "quasar-ui-bs";
import docLogo from "./assets/images/doc-logo-example.svg";
import firstTabIcon from "./assets/images/first-tab-icon.svg";

export default defineComponent({
    components: {
        BarChart,
        VariableSelect,
        DocumentationContent,
        BsButton,
        BsLayoutDefault
    },
    data() {
        return {
            chartData: [] as DataPoint[],
            selectedDefiningVariable: "",
            allData: [] as DataPoint[],
            layoutRef: undefined as undefined | typeof BsLayoutDefault,
            docLogo,
            firstTabIcon,
            definingVariables: [] as String[],
        };
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
        this.definingVariables = [...new Set(this.allData.map(item => item.definingVariable))];
      });
      this.layoutRef = this.$refs.layout as InstanceType<typeof BsLayoutDefault>;
    }
})
</script>

<style lang="scss" scoped>
.toggle-left-button {
    display: none;
}

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
    top: -12px;
    left: 10px;
}

.drawer-title {
  margin-top: 0;
  color: var(--interactions-bs-color-interaction-primary, #2B66FF);
  /* bs-font-medium-4-semi-bold */
  font-family: SourceSansPro;
  font-size: 20px;
  font-style: normal;
  font-weight: 600;
  line-height: 32px; /* 160% */
}
:deep(.bs-btn) {
    display: inline-flex;
    color: var(--text-and-icons-bs-color-text-with-background, #fff);
    padding: var(--bs-spacing-1, 4px) var(--bs-spacing-3, 12px);
    justify-content: center;
    align-items: center;
    gap: var(--bs-spacing-1, 4px);
    border-radius: var(--bs-radius-samll-200, 4px);
    background: var(--interactions-bs-color-interaction-primary, #2b66ff);
    line-height: 22px;
}
:deep(.bs-btn:hover) {
    background: var(--interactions-bs-color-interaction-hover, #143384);
}
:deep(.bs-btn:disabled) {
    color: var(--text-and-icons-bs-color-text-light, #929292);
    background: var(--interactions-bs-color-interaction-disable, #e5e5e5);
}
/* Selector style TODO move to the lib */
:deep(.q-field__native),
:deep(.q-field--auto-height.q-field--dense .q-field__control),
:deep(.q-field--auto-height.q-field--dense .q-field__native),
:deep(.q-field--dense .q-field__marginal) {
    min-height: 26px;
}
:deep(.q-field__native),
:deep(.q-field--dense .q-field__marginal) {
    height: 26px;
    padding: var(--bs-spacing-05, 2px) var(--bs-spacing-0, 0px);
    color: #333e48;
}
:deep(.q-field--dense .q-field__marginal) {
    font-size: 16px;
}

:deep(.q-field--outlined .q-field__control) {
    border-radius: var(--bs-radius-small-100, 2px);
}
:deep(.q-item__label),
:deep(.q-item__section) {
    line-height: 22px;
    font-size: 14px;
}
:deep(.bs-select__popup .q-item) {
    height: auto;
    min-height: 20px;
}
/* TODO move this to lib and fix it for now it only work if added to the container component */
:deep(.q-item) {
    height: auto !important;
    min-height: 20px !important;
}
/* TODO move  */
:deep(.dku-tiny-text) {
    /* dku-tiny-text - 10px */
    font-size: 10px;
    font-style: normal;
    font-weight: 400;
    line-height: 15px; /* 150% */
}

/* TODO move this to lib */
:deep(.bs-font-medium-1-bold) {
    /* bs-font-medium-1-bold */
    font-size: 12px;
    font-style: normal;
    font-weight: 700;
    line-height: 20px; /* 166.667% */
}
:deep(.bs-font-medium-1-normal) {
    /* bs-font-medium-1-normal */
    font-size: 12px;
    font-style: normal;
    font-weight: 400;
    line-height: 20px; /* 166.667% */
}
/* TODO move this to lib */
:deep(.bs-font-medium-3-semi-bold) {
    /* bs-font-medium-3-semi-bold */
    font-size: 16px;
    font-style: normal;
    font-weight: 600;
    line-height: 22px; /* 137.5% */
}
/* TODO move this to lib */
:deep(.bs-font-medium-2-normal) {
    /* bs-font-medium-2-normal */
    font-size: 14px;
    font-style: normal;
    font-weight: 400;
    line-height: 22px; /* 157.143% */
}

/* TODO move this to lib */
:deep(.bs-font-large-1-semi-bold) {
    font-size: 24px;
    font-style: normal;
    font-weight: 600;
    line-height: 40px; /* 166.667% */
}
/* TODO move this to lib */
:deep(.bs-font-medium-2-semi-bold) {
    /* bs-font-medium-2-semi-bold */
    font-size: 14px;
    font-style: normal;
    font-weight: 600;
    line-height: 22px; /* 157.143% */
}
/* TODO move this to lib */
:deep(.bs-font-medium-4-semi-bold) {
    /* bs-font-medium-4-semi-bold */
    font-size: 20px;
    font-style: normal;
    font-weight: 600;
    line-height: 32px; /* 160% */
}
/* TODO move this to lib */
:deep(.bs-font-medium-1-normal) {
    /* bs-font-medium-1-normal */
    font-size: 12px;
    font-style: normal;
    font-weight: 400;
    line-height: 20px; /* 166.667% */
}
/* TODO move this to lib */
:deep(.bs-font-medium-3-normal) {
    /* bs-font-medium-3-normal */
    font-size: 16px;
    font-style: normal;
    font-weight: 400;
    line-height: 22px; /* 137.5% */
}
/* TODO move this to lib */
:deep(.bs-font-small-2-normal) {
    /* bs-font-small-2-normal */
    font-size: 10px;
    font-style: normal;
    font-weight: 400;
    line-height: 18px; /* 180% */
}
/* TODO move this to lib */
:deep(.bs-font-medium-1-normal-underline) {
    /* bs-font-medium-1-normal-underline */
    font-size: 12px;
    font-style: normal;
    font-weight: 400;
    line-height: 20px; /* 166.667% */
    text-decoration-line: underline;
}
/* TODO move to lib */
:deep(.q-tab.q-tab--active) {
    background: var(
        --information-bs-color-information-background,
        #d6e1fe
    ) !important;
}
:deep(.bs-slider input) {
    width: 48px;
    height: 20px;
    padding: var(--bs-spacing-1, 4px) var(--bs-spacing-2, 8px)
        var(--bs-spacing-1, 4px) var(--bs-spacing-1, 4px);
    align-items: center;
    border: 1px solid var(--base-colors-bs-color-border-light, #e5e5e5);
    background: var(--base-colors-bs-color-background, #fff);
    color: var(--text-and-icons-bs-color-text, #333e48);
    /* bs-font-medium-1-normal */
    font-size: 12px;
    font-style: normal;
    font-weight: 400;
    line-height: 20px; /* 166.667% */
}

.bs-header-wrapper.bs-header-wrapper--hide-tab-name {
    left: 0px !important;
}
/* TODO move to lib maybe */
.bs-truncate-text {
    width: 100%; /* or whatever width you prefer */
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}
.q-item {
    height: auto !important;
    min-height: 22px !important;
    padding: 0 8px;
}
.bs-select__popup .q-item.q-item--active {
    background-color: #fff;
}

.bs-select__popup .q-item {
    /* bs-font-medium-2-normal */
    font-size: 14px;
    font-style: normal;
    font-weight: 400;
    line-height: 22px; /* 157.143% */
}
.bs-select__popup .q-item.q-manual-focusable.q-manual-focusable--focused {
    background-color: var(--interactions-bs-color-interaction-primary, #2b66ff);
}
.q-field--outlined.q-field--readonly .q-field__control:before {
    border-style: solid;
}
.bs-tab-title {
    /* visibility: hidden; */
    max-width: calc(var(--bs-drawer-width) - 45px) !important;
}
.bs-header-wrapper.bs-header-wrapper--hide-tab-name {
    left: 0;
}
.disable {
    color: var(--interactions-bs-color-interaction-disable, #e5e5e5);
}
/* TODO move to lib */
.text-positive-alert {
    color: #0b590b !important;
}
.bg-positive-alert {
    background-color: #d7f0d6 !important;
}
.text-negative-alert {
    color: #ce1228 !important;
}
.bg-negative-alert {
    background-color: #f9e3e5 !important;
}
.bg-interactions-bs-color-interaction-selected {
    background: var(--interactions-bs-color-interaction-selected, #214ab5);
}
.text-interactions-bs-color-interaction-selected {
    color: var(--interactions-bs-color-interaction-selected, #214ab5);
}
/* TODO move this to lib */
.bs-font-medium-1-semi-bold {
    /* bs-font-medium-1-semi-bold */
    font-size: 12px;
    font-style: normal;
    font-weight: 600;
    line-height: 20px; /* 166.667% */
}
/* TODO move this to lib */
.bs-alert-notification {
    min-width: 600px;
    border-radius: var(--bs-radius-messages, 0px);
    box-shadow: none;
}

</style>
