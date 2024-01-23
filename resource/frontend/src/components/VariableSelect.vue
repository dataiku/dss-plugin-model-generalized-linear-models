<template>
    <div class="bs-clearable-field-container">
      <div
        v-if="label !== undefined"
        class="dds-caption-400 bs-clearable-field-main-label"
      >
        {{ label }}
        <BsHelp v-if="usingBsHelp()" side="right">
          <slot v-if="$slots.help" name="help"></slot>
          <span v-else>{{ helpMessage }}</span>
        </BsHelp>
      </div>
      <!-- <BsSelect bs-label="my select" :options="options" v-model="selectedVal">
      </BsSelect> -->
      <!-- <BsSelect
        :modelValue="selectedTarget"
        :options="options"
        ></BsSelect> -->
        <QSelect
        :modelValue="selectedTarget"
        :options="options"
        ></Qselect>
    </div>
  </template>
  <script lang="ts">
  import { defineProps, useSlots } from "vue";
  import BsHelp from "./BsHelp.vue";
import { BsSelect } from "quasar-ui-bs";
import { QSelect } from "quasar";
  
  export default {
    props: {
      label: {
              type: String,
              required: true,
          },
      helpMessage: {
              type: String,
              required: true,
          },
        selectedTarget: {
            type: String,
            required: true,
        },
        options: {
            type: Array<String>,
            required: true,
        }
    },
    components: {
    BsHelp,
    BsSelect,
    QSelect
},
    data() {
      return {
        slots: useSlots(),
        selectedVal: ""
      }
    },
    methods: {
      usingBsHelp() {
        return !!(this.helpMessage || this.slots.help);
      }
    }
  }
  </script>
  <style lang="scss" scoped>
  .bs-clearable-field-container {
    display: flex;
    flex-direction: column;
  
    gap: 4px;
  }
  
  .bs-clearable-field-main-label {
    display: flex;
    align-items: center;
  
    gap: 5px;
  }
  </style>
  