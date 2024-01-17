<template>
  <div>
    <div class="bs-font-medium-2-normal" v-if="label" style="padding-bottom: 4px">
      {{ label }}
    </div>
    <div :style="{ 'max-width': '300px' }" class="bs-selection-content">
      <QSelect
        ref="select"
        v-model="selectedVariables"
        :options="options"
        clear-icon="clear"
        multiple
        use-chips
        use-input
        dense
        outlined
        @filter="filterFn"
        input-debounce="0"
        :disable="disabled"
        v-bind="$attrs"
        dropdown-icon="expand_more"
        :popup-content-style="popupStyle"
      >
        <!-- Templates for selected item and options -->
        <template #selected-item></template>
        <template #before-options>
          <q-item v-ripple dense class="bs-font-medium-2-normal bs-selector-dropdown-item">
            <q-item-section
              @click="toggleAll"
              class="bs-selector-item-section bs-selector-section--select-all"
              style="padding: 8px; cursor: pointer"
            >
              <q-checkbox
                :model-value="allSelected"
                :indeterminate="isSomeSelected"
                @click="toggleAll"
                size="24px"
              ></q-checkbox>
              <q-item-label class="bs-clearable-field-option-label">Select All</q-item-label>
            </q-item-section>
          </q-item>
        </template>
        <template #option="props">
          <q-item
            v-ripple
            padding="0"
            v-bind="props.itemProps"
            @click="props.toggleOption(props.opt)"
            class="bs-font-medium-2-normal bs-selector-dropdown-item"
          >
            <q-item-section class="bs-selector-item-section">
              <q-checkbox
                size="24px"
                :model-value="props.selected"
                class="bs-clearable-field-custom-size-checkbox"
                @update:model-value="props.toggleOption(props.opt)"
              ></q-checkbox>
              <q-item-label class="bs-clearable-field-option-label"
                ><BSTruncatedText :tooltip-content="props.opt">
                  {{ props.opt }}</BSTruncatedText
                ></q-item-label
              >
            </q-item-section>
          </q-item>
        </template>
      </QSelect>

      <BsWarning v-if="showWarning" :text="warningText"></BsWarning>

      <div>
        <div
          class="bs-selected-items-section"
          v-if="selectedVariables && selectedVariables.length > 0"
        >
          <!-- Selected Items Display -->
          <div class="bs-selected-items-container">
            <div
              v-if="!showAllSelected"
              v-for="(item, index) in displayedItems"
              :key="index"
              class="bs-font-small-2-normal bs-selected-item"
            >
              <BSTruncatedText :tooltip-content="item"> {{ item }}</BSTruncatedText>
              <BsIcon name="close" @click="deleteItem(item)"></BsIcon>
            </div>

            <div v-if="showAllSelected" class="bs-selected-items-container bs-all-selected">
              <div
                v-for="item in selectedVariables"
                :key="item"
                class="bs-font-small-2-normal bs-selected-item"
              >
                <BSTruncatedText :tooltip-content="item"> {{ item }}</BSTruncatedText>
                <BsIcon name="close" @click="deleteItem(item)"></BsIcon>
              </div>
            </div>
          </div>
          <BsButton
            class="bs-font-medium-1-normal-underline bs-clear-all"
            unelevated
            flat
            no-caps
            padding="4"
            @click="clearAllSelection"
          >
            Clear All
          </BsButton>
        </div>
        <div
          class="bs-font-medium-1-normal bs-view-more"
          v-if="selectedVariables.length > 4"
          @click="showAllSelected = !showAllSelected"
        >
          View {{ selectedVariables.length - 4 }}
          {{ showAllSelected ? 'less' : 'more' }}
          <BsIcon :name="!showAllSelected ? mdiChevronDown : mdiChevronUp"></BsIcon>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { BsIcon } from 'quasar-ui-bs'
import { mdiChevronDown, mdiChevronUp } from '@quasar/extras/mdi-v6'
import BSTruncatedText from './BsTruncatedText.vue'
import BsWarning from './BsWarning.vue'
import { isEqual } from 'lodash'
import { QSelect, QItem, QItemSection } from 'quasar'

export default defineComponent({
  name: 'BSMultiSelect',
  components: {
    QSelect,
    QItem,
    QItemSection,
    BsWarning,
    BsIcon,
    BSTruncatedText
  },
  props: {
    disabled: Boolean,
    allOptions: {
      type: Array<string>,
      required: true
    },
    modelValue: {
      type: Array<string>,
      default: () => []
    },
    showWarning: {
      type: Boolean,
      default: false
    },
    warningText: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    infoText: String
  },
  emits: ['update:modelValue'],
  data() {
    return {
      mdiChevronDown,
      mdiChevronUp,
      selectedVariables: [] as string[],
      options: [] as string[],
      showAllSelected: false,
      selectAllChecked: false,
      popupStyle: {}
    }
  },
  watch: {
    'selectedVariables.length'() {
      this.$emit('update:modelValue', this.selectedVariables)
    },
    selectedVariables(newVal, oldVal) {
      if (!isEqual(newVal, oldVal)) {
        this.$emit('update:modelValue', this.selectedVariables)
      }
    },
    modelValue(newValue) {
      this.selectedVariables = newValue
    }
  },
  mounted() {
    this.selectedVariables = this.modelValue
    const selectRef = this.$refs.select as InstanceType<typeof QSelect>
    if (selectRef) {
      this.popupStyle = {
        width: selectRef.$el.offsetWidth,
        maxWidth: selectRef.$el.offsetWidth,
        wordBreak: 'break-all'
      }
    }
  },
  computed: {
    displayedItems(): string[] {
      return this.selectedVariables.slice(0, 4)
    },
    allSelected(): boolean {
      const countSelected = this.selectedVariables.reduce((prev, curr) => {
        if (this.options.indexOf(curr) >= 0) {
          return prev + 1
        } else {
          return prev
        }
      }, 0)
      return countSelected === this.options.length
    },
    isSomeSelected(): boolean {
      return this.selectedVariables.length > 0 && !this.allSelected
    }
  },
  methods: {
    filterFn(val: string, update: any) {
      update(() => {
        const needle = val.toLowerCase()
        this.options = this.allOptions.filter((v) => v.toLowerCase().indexOf(needle) > -1)
      })
    },
    clearAllSelection() {
      this.selectedVariables = []
    },
    deleteItem(itemToDelete: string) {
      this.selectedVariables = this.selectedVariables.filter((item) => item !== itemToDelete)
    },
    toggleAll() {
      if (this.allSelected) {
        this.selectedVariables = this.selectedVariables.filter(
          (el) => this.options.indexOf(el) === -1
        )
      } else {
        this.options.forEach((option) => {
          if (this.selectedVariables.indexOf(option) === -1) {
            this.selectedVariables.push(option)
          }
        })
      }
    }
  }
})
</script>

<style lang="scss" scoped>
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
.bs-font-medium-2-normal {
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 22px;
}
.bs-font-medium-1-normal {
  font-size: 12px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px;
}
.bs-font-small-2-normal {
  font-size: 10px;
  font-style: normal;
  font-weight: 400;
  line-height: 18px;
}
:deep(.q-field--outlined .q-field__control:before) {
  border-radius: var(--bs-radius-small-100, 2px);
  border: 1px solid #cccccc;
}
.bs-selected-items-section {
  display: flex;
  align-items: stretch;
}
.bs-selected-items-container {
  display: flex;
  flex-wrap: wrap;
  gap: var(--bs-spacing-1, 4px);
  align-items: center;
  width: 100%;
  overflow-x: hidden;
  border-right: solid 1px var(--base-colors-bs-color-border-light, #e5e5e5);
}
.bs-all-selected {
  max-height: 500px;
  overflow-y: auto;
}
.bs-selected-item {
  color: var(--text-and-icons-bs-color-text-with-background, #fff) !important;
  display: flex;
  padding: var(--bs-spacing-0, 0px) var(--bs-spacing-1, 4px);
  justify-content: center;
  align-items: center;
  gap: var(--bs-spacing-1, 4px);
  border-radius: 4px;
  background: var(--brand) !important;
  max-width: calc(100% - 30px);
}
.bs-view-more {
  color: var(--text-and-icons-bs-color-text, #333e48);
  display: block;
  margin-top: 8px;
  margin-bottom: 8px;
  cursor: pointer;
}
.bs-clear-all {
  width: 53px;
  margin-left: auto;
  padding: var(--bs-spacing-0, 0px) var(--bs-spacing-1, 4px);
  align-self: center;
  color: var(--text-and-icons-bs-color-text, #333e48);
}

.bs-selection-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.bs-selector-dropdown-item {
  padding: 0 !important;
  min-height: 0 !important;
  /* * {
      pointer-events: none;
  } */
}
.bs-selector-item-section {
  padding: 2px 11px !important;
  display: flex;
  flex-direction: row !important;
  align-items: center;
  justify-content: flex-start;
  min-height: 0 !important;
  gap: 11px;
  min-width: 0 !important;
  max-width: 85%;
  flex-wrap: nowrap;
}
.q-item--active {
  color: var(--text-and-icons-bs-color-text, #333e48) !important;
}
.bs-selector-section--select-all {
  min-height: 36px !important;
  color: var(--text-and-icons-bs-color-text, #333e48) !important;
}
</style>
<style>
.bs-select__popup {
  max-height: 500px !important;
  overflow-y: scroll;
  transition: max-height 0.5s;
}
</style>
