<template>
  <div class="q-pa-sm card" :class="{ selected: isSelected }" @click="emits('update:conv', id)">
    <div class="row items-center justify-between">
      <div class="column">
        <div style="max-width: 100%">
          <div class="title">
            {{ title }}
            <BsTooltip>{{ title }}</BsTooltip>
          </div>
        </div>
      </div>
      <div>
        <q-icon
          :name="`img:${trashIcon}`"
          size="xs"
          v-if="isSelected"
          @click="openDialogDelete = true"
        >
          <DeleteDialog
            :open="openDialogDelete"
            :title="t('delete_item_title')"
            :text="t('delete_item_warning', { title: title })"
            @confirm="emits('delete:conv', props.id)"
            @cancel="openDialogDelete = false"
          />
        </q-icon>
        <div v-else></div>
      </div>
    </div>
    <div class="date row" style="justify-content: space-between">
      <div>
        {{ formattedDate.split('-')[0] }}
      </div>
      <div>
        {{ formattedDate.split('-')[1] }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import trashIcon from '@/assets/icons/trash.svg'
import { computed, ref } from 'vue'
import DeleteDialog from './DeleteDialog.vue'
import { useI18n } from 'vue-i18n'

const openDialogDelete = ref(false)

const { t } = useI18n()

function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp * 1000)
  const full = `${date.toLocaleString('default', {
    month: 'short'
  })} ${date.getDate()}, ${date.getFullYear()}`
  const fullWithTimestamp = `${full} - ${date.toLocaleTimeString('default', {
    hour: '2-digit',
    minute: '2-digit'
  })}`

  return fullWithTimestamp
}

const props = defineProps<{
  title: string
  date: number
  id: string
  isSelected: boolean
}>()

const formattedDate = computed(() => {
  return formatTimestamp(props.date)
})

const emits = defineEmits<{
  (e: 'update:conv', id: string): void
  (e: 'delete:conv', id: string): void
}>()
</script>

<style scoped lang="scss">
.column {
  max-width: 90%;
  gap: 8px;
  margin-bottom: 8px;
}
.card {
  // border-radius: 4px;
  // box-shadow: 0px 4px 2px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid var(--light_grey, #eaeff3);
  background: #fff;
  cursor: pointer;
}

.title {
  color: #333; /* .dds-caption-400 */
  font-family: SourceSansPro;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 15px; /* 125% */
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.date {
  color: var(--greyscale-grey-lighten-4, #999);
  /* .dds-caption-400 */
  font-family: Source Sans Pro;
  font-size: 12px;
  font-style: normal;
  font-weight: 400;
  line-height: 15px;
}

.selected {
  // background: #f5f5f5;
  background: var(--bg-examples-brand);
}
</style>
