<template>
  <div class="column" style="margin-left: 4px">
    <div v-for="(tagsList, tagName) in tags" :key="tagName">
      <div class="tag-text">{{ tagName }}</div>
      <SourceTags :tags="tagsList" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import SourceTags from './SourceTags.vue'

const props = defineProps<{
  tags: Record<string, any[]>
}>()
const { t } = useI18n()

const expanded = ref(false)
</script>

<style scoped lang="scss">
.tag-text {
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
.tags-expansion-item {
  margin-top: 10px;
  font-size: 12px;
  font-weight: bold;
  color: #444;
}

:deep(.q-item) {
  padding: 4px;
}
:deep(.q-item__section--side > .q-icon) {
  font-size: 16px;
}
</style>
