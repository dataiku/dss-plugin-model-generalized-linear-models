<template>
  <div class="bs-warning" :class="warningType">
    <q-icon :name="iconName" :alt="iconAlt" size="20px" />
    <div class="bs-warning-text-container">
      {{ text }}
      <slot></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { mdiInformationOutline } from '@quasar/extras/mdi-v6'
import { mdiCloseCircleOutline } from '@quasar/extras/mdi-v6'
export default defineComponent({
  name: 'BsWarning',
  props: {
    text: String,
    warningType: {
      type: String,
      default: 'info' // default type is set to 'info'
    },
    closable: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    iconName(): string {
      switch (this.warningType) {
        case 'info':
          return mdiInformationOutline
        case 'error':
          return mdiCloseCircleOutline
        case 'success':
          return 'check'
        case 'settings':
          return 'settings'
        default:
          return mdiInformationOutline
      }
    },
    iconAlt(): string {
      return this.warningType + ' icon'
    }
  }
})
</script>

<style scoped>
.bs-warning {
  display: flex;
  max-width: 600px;
  justify-content: space-between;
  /* width: 100%; */
  padding: var(--bs-spacing-3, 12px) var(--bs-spacing-4, 16px);
  align-items: center;
  gap: var(--bs-spacing-2, 8px);
}

.bs-warning.info,
.bs-warning.settings {
  color: var(--information-bs-color-information, #27468e);
  border-left: 4px solid var(--information-bs-color-information, #27468e);
  background-color: var(--information-bs-color-information-background, #d6e1fe);
}
.bs-warning-text-container {
  flex-grow: 1;
  display: flex;
  align-items: center;
  gap: var(--bs-spacing-2, 8px);
}
.bs-warning.success {
  color: var(--status-bs-color-status-success, #0b590b);
  border-left: 6px solid #0b590b;
  background-color: rgba(0, 128, 0, 0.1);
}

.bs-warning.error {
  color: var(--status-bs-color-status-error, #ce1228);
  border-left: 6px solid #ce1228;
  background-color: rgba(233, 65, 43, 0.1);
}
</style>
