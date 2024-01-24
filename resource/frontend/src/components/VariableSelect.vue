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
    <BsSelect v-bind="$attrs">
      <template v-for="(_, slot) in $slots" v-slot:[slot]="scope">
        <slot :name="slot" v-bind="scope || {}" />
      </template>
    </BsSelect>
  </div>
</template>
<script lang="ts">
import { defineProps, useSlots } from "vue";
import BsHelp from "./BsHelp.vue";

export default {
  props: {
    label: {
            type: String,
            required: true,
        },
    helpMessage: {
            type: String,
            required: true,
        }
  },
  components: {
    BsHelp
  },
  data() {
    return {
      slots: useSlots()
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
