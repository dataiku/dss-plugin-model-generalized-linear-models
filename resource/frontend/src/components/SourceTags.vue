<template>
  <div class="tags">
    <div
      v-for="(tag, index) in tags"
      :key="index"
      @click="toggleTag(index)"
      :class="['tag-item', { expanded: expandedTags[index] }]"
    >
      {{ tag }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  tags: any[]
}>()
const expandedTags = ref({} as any)

function toggleTag(index: number) {
  expandedTags.value[index] = !expandedTags.value[index]
}
</script>

<style lang="scss" scoped>
.tags {
  display: flex;
  flex-wrap: wrap;
  padding: var(--bs-spacing-0, 0px);

  align-items: center;
  gap: var(--bs-spacing-1, 4px);
}

.tag-item {
  border-radius: var(--bs-radius-medium-200, 16px);
  background: #f28c38;
  padding: var(--bs-spacing-05, 2px) var(--bs-spacing-3, 12px);
  color: var(--text-and-icons-bs-color-text-with-background, #fff);
  font-family: SourceSansPro;
  font-size: 11px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 181.818% */
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-height: 24px;
  cursor: pointer;
  transition: max-height 0.3s ease;
}
.expanded {
  white-space: normal;
  overflow: visible;
  max-width: none;
  max-height: none;
}
</style>
