<template>
    <BsLayoutDefault ref="layout" :left-panel-width="350">
      <template v-for="tabInfo in tabs" :key="tabInfo.name">
            <BsTab :name="tabInfo.name" :docTitle="tabInfo.docTitle">
                <BsTabIcon>
                    <img :src="tabInfo.icon" :alt="`${tabInfo.name} Icon`" />
                </BsTabIcon>
                <BsDrawer>
                    <component
                        :is="tabInfo.drawerComponent"
                        v-bind="tabInfo.drawerProps"
                        @update:loading="updateLoading"
                        @navigate-tab="goToTab"
                    />
                </BsDrawer>
                <BsContent>
                    <template
                        v-if="
                            tabInfo.contentComponent && !tabInfo.showEmptyState
                        "
                    >
                        <component
                            :is="tabInfo.contentComponent"
                            v-bind="tabInfo.contentProps"
                            @update:loading="updateLoading"
                            @navigate-tab="goToTab"
                        />
                    </template>
                    <template v-else>
                        <EmptyState
                            :title="tabInfo.emptyState.title"
                            :subtitle="tabInfo.emptyState.subtitle"
                        />
                    </template>
                </BsContent>
            </BsTab>
        </template>

      <!-- <ModelTrainingTab
        @update-models="updateModels">
      </ModelTrainingTab>
      <OneWayTab
      :reload-models="reloadModels">
      </OneWayTab>
      <VariableLevelStatsTab
      :reload-models="reloadModels">
      </VariableLevelStatsTab>
      <LiftChartTab
      :reload-models="reloadModels">
      </LiftChartTab>
      <ModelComparisonTab
      :reload-models="reloadModels">
      </ModelComparisonTab> -->

    </BsLayoutDefault>
</template>

<script lang="ts">
import LiftChartTab from './components/LiftChartTab.vue';
import ModelTrainingTab from './components/ModelTrainingTab.vue';
import ModelComparisonTab from './components/ModelComparisonTab.vue';
import OneWayTab from './components/OneWayTab.vue';
import VariableLevelStatsTab from './components/VariableLevelStatsTab.vue';
import { BsLayoutDefault } from "quasar-ui-bs";
import { defineComponent } from "vue";
import { useLoader } from "./composables/use-loader";
import firstTabIcon from "./assets/images/first-tab-icon.svg";

export default defineComponent({
    components: {
        ModelTrainingTab,
        ModelComparisonTab,
        OneWayTab,
        VariableLevelStatsTab,
        LiftChartTab,
    },
    data() {
    return {
        reloadModels: false as boolean,
        chartData: null,
        loading: false as boolean,
      }
    },
    methods: {
      updateModels(){
        this.reloadModels = !this.reloadModels;
      },
      updateLoading(newVal: boolean) {
            this.loading = newVal;
        },
        goToTab(index: number) {
            const layout = this.$refs.layout as InstanceType<
                typeof BsLayoutDefault
            >;
            if (layout) {
                layout.tabIndex = index;
            }
        },
    },
    watch: {
      loading(newVal) {
          if (newVal) {
              useLoader("Loading data..").show();
          } else {
              useLoader().hide();
          }
      },
    },
    computed: {
      tabs() {
            return [
                {
                    name: "One-Way Variable",
                    docTitle: "Parameters Analyzer",
                    icon: firstTabIcon,
                    headerInfo: {
                    },
                    drawerComponent: "OneWayTab",
                    contentComponent: "OneWayTabContent",
                    contentProps: {},
                    drawerProps: {
                      reloadModels: this.reloadModels
                    },
                    showEmptyState: this.chartData,
                    emptyState: {
                        title: "One-Way Variable",
                        subtitle:
                            "Select variable in the left column to create chart",
                    },
                }
            ];
        }
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
</style>
