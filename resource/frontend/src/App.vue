<template>
    <BsLayoutDefault ref="layout">
      <ModelTrainingTab>
      </ModelTrainingTab>
      <OneWayTab>
      </OneWayTab>
      <VariableLevelStatsTab>
      </VariableLevelStatsTab>
      <LiftChartTab>
      </LiftChartTab>
      <ModelComparisonTab>
      </ModelComparisonTab>

    </BsLayoutDefault>
</template>

<script lang="ts">
import LiftChartTab from './components/LiftChartTab.vue';
import ModelTrainingTab from './components/ModelTrainingTab.vue';
import ModelComparisonTab from './components/ModelComparisonTab.vue';
import OneWayTab from './components/OneWayTab.vue';
import VariableLevelStatsTab from './components/VariableLevelStatsTab.vue';
import { defineComponent } from "vue";
export default defineComponent({
    components: {
        ModelTrainingTab,
        ModelComparisonTab,
        OneWayTab,
        VariableLevelStatsTab,
        LiftChartTab,
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
