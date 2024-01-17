<template>
  <q-input
    :model-value="modelValue"
    @update:model-value="updateModelValue"
    outlined
    dense
    class="query-input"
    :placeholder="inputPlaceholder"
    @keydown.enter="(e : Event) => handleEnterKey(e)"
    :disable="isLoading"
  >
    <template v-slot:append>
      <q-icon
        v-if="!isLoading"
        name="send"
        class="cursor-pointer send-icon"
        @click="submit"
        size="xs"
        :style="activeStyle"
      />
      <q-spinner v-else color="var(--brand)" size="xs" />
    </template>
  </q-input>
</template>
<script lang="ts">
export default {
  props: {
    isLoading: Boolean,
    placeholder: String,
    modelValue: String
  },
  methods: {
    submit() {
      this.$emit('submit')
    },
    handleEnterKey: function (event: any) {
      event.stopPropagation()
      event.preventDefault()
      this.submit()
    },
    updateModelValue(value: string | number | null) {
      this.$emit('update:model-value', value)
    }
  },
  computed: {
    inputPlaceholder() {
      return this.placeholder || this.$t('questionPlaceholder')
    },
    activeStyle() {
      if (this.isLoading) {
        return {
          color: '#CCCCCC',
          cursor: 'wait !important'
        }
      } else {
        if (this.modelValue) {
          return {
            color: 'var(--brand)',
            cursor: 'pointer'
          }
        } else {
          return {
            color: '#CCCCCC',
            cursor: 'not-allowed !important'
          }
        }
      }
    }
  }
}
</script>
<style scoped>
.query-input {
  width: 100%;
}
.send-icon {
  margin-bottom: 4px;
  transform: rotate(-38.48deg);
}
</style>
