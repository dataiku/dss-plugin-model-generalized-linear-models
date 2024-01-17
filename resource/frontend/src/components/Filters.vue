<template>
  <q-expansion-item
    :label="$t('filters')"
    v-model="expanded"
    header-class="expansion-item"
    switch-toggle-side
    class="filters-expansion-item"
  >
    <div class="column" style="margin-left: 4px">
      <div v-for="(tags, filterName) in filters" :key="filterName">
        <div class="filter-text">{{ filterName }}</div>
        <FilterTags :tags="tags" />
      </div>
    </div>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import FilterTags from './FilterTags.vue'

const props = defineProps<{
  filters: Record<string, any[]>
}>()
const { t } = useI18n()

const expanded = ref(false)
</script>

<style scoped lang="scss">
.filter-text {
  color: #444;

  font-family: Source Sans Pro;
  font-size: 11px;
  font-style: normal;
  font-weight: 600;
  line-height: 20px; /* 181.818% */
}
.expansion-item {
  font-style: normal;
  font-weight: 600;
  font-size: 20px;
  line-height: 15px;
  color: #666666;
  width: 100%;
}
.filters-expansion-item {
  margin-top: 10px;
  font-size: 12px;
  font-weight: bold;
  /* color: teal; */
  margin-left: -4px;
  color: #444;
}

:deep(.q-item) {
  padding: 4px;
}
:deep(.q-item__section--side > .q-icon) {
  font-size: 16px;
}
</style>
