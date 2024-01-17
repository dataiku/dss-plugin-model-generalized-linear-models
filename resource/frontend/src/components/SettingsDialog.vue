<template>
  <q-btn
    flat
    dense
    no-caps
    no-wrap
    color="primary"
    @click="openSettingsDialog = true"
    size="md"
    v-if="!noKnowledgeBankSetup"
  >
    <q-icon size="18px" style="margin-right: 2px" color="primary">
      <SettingsIcon color="#3B99FC" />
    </q-icon>

    {{ $t('settings') }}
    <q-icon size="16px" v-if="knowledgeBankId" style="margin-left: 4px">
      <DbIcon color="#3B99FC" />
    </q-icon>
    <q-badge v-if="knowledgeBankId" rounded floating color="#2B66FF" style="font-size: 10px">
      {{ badgeLabel }}
    </q-badge>
    <q-dialog persistent :model-value="openSettingsDialog">
      <q-card style="width: 600px">
        <q-card-section>
          <div class="row items-center q-gutter-x-sm justify-between">
            <div class="row items-center no-wrap q-gutter-x-sm">
              <q-icon size="21px">
                <SettingsIcon />
              </q-icon>
              <div class="dku-grand-title">{{ t('settings') }}</div>
            </div>
            <q-icon size="21px" name="close" style="cursor: pointer" @click="cancel"></q-icon>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-section>
          <template v-if="setup.filtersConfig">
            <div style="margin-left: -12px">
              <QToggle
                v-model="useKnowledgeBank"
                :disable="noKnowledgeBankSetup"
                :class="noKnowledgeBankSetup ? 'disabled' : ''"
                >{{ $t('use_knowledge_bank') }}{{ setup.knowledgeBank?.label ? ': ' : ''
                }}<b>{{ setup.knowledgeBank?.label }}</b></QToggle
              >
            </div>
            <div class="flex-column-20" v-if="useKnowledgeBank">
              <div class="row items-center no-wrap q-gutter-x-sm" style="margin-top: 10px">
                <q-icon size="16px">
                  <FilterIcon />
                </q-icon>
                <div class="dku-medium-title">{{ t('filters') }}</div>
              </div>
              <div
                style="overflow-y: scroll"
                v-if="Object.keys(setup.filtersConfig.filter_options).length"
              >
                <BSMultiSelect
                  v-for="(options, column) in setup.filtersConfig.filter_options"
                  :key="column"
                  :label="t('select_label', { item: column })"
                  :all-options="options"
                  :model-value="filters[column]"
                  @update:model-value="(event) => updateSelectedOption(column, event)"
                >
                </BSMultiSelect>
              </div>
              <BsWarning type="info" :text="t('empty_filters_text')" v-else> </BsWarning>
            </div>
          </template>

          <template v-else>
            <BsWarning type="info" :text="t('no_filters_text')"> </BsWarning>
          </template>
        </q-card-section>
        <q-card-actions align="right">
          <bs-button class="bs-btn-flat-danger dku-text" unelevated flat @click="cancel">
            {{ t('cancel') }}</bs-button
          >
          <bs-button class="bs-btn-flat dku-text" unelevated flat @click="apply">{{
            t('apply')
          }}</bs-button>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-btn>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, computed } from 'vue'
import BsWarning from './BsWarning.vue'
import BSMultiSelect from './BsMultiSelect.vue'
import { useSettings } from './composables/use-settings'
import { useUI } from './composables/use-ui'
import FilterIcon from './icons/FilterIcon.vue'
import SettingsIcon from './icons/SettingsIcon.vue'
import DbIcon from './icons/DbIcon.vue'
import { QToggle } from 'quasar'
const { t } = useI18n()

const openSettingsDialog = ref(false)
const { setup } = useUI()
const { filtersSelections: selection, knowledgeBankSelection: knowledgeBankId } = useSettings()
const useKnowledgeBank = ref(knowledgeBankId.value ? true : false)
const filters = ref({ ...selection.value })
function updateSelectedOption(column: string, newVal: string[]) {
  filters.value[column] = newVal
}

const noKnowledgeBankSetup = computed(() => {
  return !setup.value.knowledgeBank
})
const badgeLabel = computed(() => {
  if (!useKnowledgeBank.value) return 0
  let count = 0
  for (const key in selection.value) {
    if (selection.value[key] && selection.value[key].length > 0) count++
  }
  return count
})
const cancel = () => {
  useKnowledgeBank.value = knowledgeBankId.value !== null
  filters.value = { ...selection.value }
  openSettingsDialog.value = false
}
const apply = () => {
  if (useKnowledgeBank.value) {
    knowledgeBankId.value = setup.value.knowledgeBank!.id
  } else {
    knowledgeBankId.value = null
  }
  selection.value = { ...filters.value }
  openSettingsDialog.value = false
}
</script>

<style scoped lang="scss">
.flex-column-20 {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.disabled {
  color: grey;
  opacity: 0.7 !important;
}
</style>
