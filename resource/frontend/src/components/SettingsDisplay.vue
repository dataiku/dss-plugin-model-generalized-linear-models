<template>
  <div class="column q-gutter-y-sm">
    <div class="row items-center q-gutter-x-xs">
      <q-icon><FilterIcon /></q-icon>
      <span class="bs-font-medium-2-semi-bold">{{ t('applied_filters') }}</span>
    </div>
    <div class="row q-gutter-x-sm">
      <q-btn v-for="filterName in visibleFilters" flat dense no-caps :key="filterName">
        <div class="row items-center q-gutter-x-xs">
          {{ filterName }}
          <q-icon size="14px">
            <ChevronDownIcon v-if="active != filterName" />
            <ChevronUpIcon v-else />
          </q-icon>
        </div>
        <q-popup-proxy
          @before-show="active = filterName"
          @before-hide="active = undefined"
          :offset="[5, 5]"
          style="min-width: 270px"
        >
          <q-card class="card-container">
            <q-card-section>
              <div class="bs-selected-items-container">
                <div
                  class="bs-font-small-2-normal bs-selected-item"
                  v-for="item in filters[filterName]"
                  :key="item"
                >
                  {{ item }}
                </div>
              </div>
            </q-card-section>
          </q-card>
        </q-popup-proxy>
      </q-btn>
    </div>
    <div v-if="hasShowAll">
      <q-btn flat dense no-caps @click="showAll = !showAll">
        <div v-if="!showAll" class="row items-center q-gutter-x-xs">
          {{ t('see_more_filters', { count: remainingFiltersNumber }) }}
          <q-icon size="14px">
            <ChevronDownIcon />
          </q-icon>
        </div>
        <div v-else class="row items-center q-gutter-x-xs">
          {{ t('see_less_filters') }}
          <ChevronUpIcon />
        </div>
      </q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import FilterIcon from './icons/FilterIcon.vue'
import { computed, ref } from 'vue'
import ChevronUpIcon from './icons/ChevronUpIcon.vue'
import ChevronDownIcon from './icons/ChevronDownIcon.vue'

const { t } = useI18n()
const props = defineProps<{
  filters: Record<string, any[]>
}>()

const showAll = ref(false)

const active = ref<string>()

const filtersNames = computed(() => {
  const names: string[] = []
  if (props.filters) {
    for (const key in props.filters) {
      if (props.filters[key] && props.filters[key].length > 0) {
        names.push(key)
      }
    }
  }
  return names
})

const visibleFilters = computed(() => {
  if (showAll.value) return filtersNames.value
  else {
    if (filtersNames.value.length > 6) return filtersNames.value.slice(0, 6)
    return filtersNames.value
  }
})

const hasShowAll = computed(() => {
  return filtersNames.value.length > 6
})

const remainingFiltersNumber = computed(() => {
  if (hasShowAll.value) {
    return filtersNames.value.length - 6
  } else {
    return null
  }
})
</script>

<style scoped lang="scss">
.bs-font-medium-2-semi-bold {
  color: var(--text-and-icons-bs-color-text, #333e48);
  /* bs-font-medium-2-semi-bold */
  font-family: SourceSansPro;
  font-size: 14px;
  font-style: normal;
  font-weight: 600;
  line-height: 22px; /* 157.143% */
}

.card-container {
  border-radius: var(--bs-radius-small-100, 2px);

  background: #fff;

  /* bs-shadow-large-400 */
  box-shadow: 0px 2px 6px 2px rgba(0, 0, 0, 0.3);
}

.bs-selected-items-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--bs-spacing-1, 4px);
  align-items: center;
  width: 100%;
  border-right: solid 1px var(--base-colors-bs-color-border-light, #e5e5e5);
  max-height: 500px;
  overflow-y: scroll;
}

.bs-selected-item {
  color: var(--text-and-icons-bs-color-text-with-background, #fff) !important;
  display: flex;
  padding: var(--bs-spacing-0, 0px) var(--bs-spacing-1, 4px);
  justify-content: center;
  align-items: center;
  gap: var(--bs-spacing-1, 4px);
  border-radius: 4px;
  background: var(--interactions-bs-color-interaction-selected, #214ab5);
}

.bs-font-small-2-normal {
  font-size: 10px;
  font-style: normal;
  font-weight: 400;
  line-height: 18px;
}
</style>
