<template>
  <div class="column items-center justify-center content-container" :class="{ loading: loadingQuestion }">
    <div class="scroll-area" ref="scrollAreaRef">
      <div class="items-center justify-center">
        <div v-for="(item, index) in currentConversation?.data" :key="item.id"
          class="history items-center justify-center">
          <QuestionCard :query="item.query">
            <Filters :filters="item.filters" v-if="item.filters" />
          </QuestionCard>
          <AnswerCard v-if="item.query && item.query !== ''" :answer="item.answer" :feedback="item.feedback"
            :feedback-options-negative="setup.feedbackNegativeChoices ?? []"
            :feedback-options-positive="setup.feedbackPositiveChoices ?? []"
            @update:feedback="(value) => logFeedback(item.id, item, value)" :typing-effect-on="false"
            :error-state="errorState">
            <Sources class="self-start" :sources="item.sources" :project-key="setup.projectKey"
              :folder-id="setup.docsFolderId" v-if="item.sources && item.sources.length > 0"
              @update:expanded="(value) => handleSourceExpanded(index, value)" />
          </AnswerCard>
        </div>
      </div>
    </div>

    <div class="footer-section">
      <UserInput ref="userInputAreaRef" id="user-query-container" :input-placeholder="inputPlaceholder"
        :value="currentData.query" :loading="loadingQuestion" @send="sendQuestion" @enterkey="sendQuestion" @update:value="(value) => {
          currentData.query = value
        }
          " @size-change="resizeScrollArea" />
    </div>

    <q-btn v-if="!isNew && currentConversation?.data && currentConversation.data.length > 0" flat dense no-caps no-wrap
      color="primary" class="clear-history-btn" @click="openDeleteDialog = true" size="md">
      <q-icon :name="`img:${trashIcon}`" size="18px" style="margin-right: 2px"></q-icon>{{ $t('clearHistory') }}

      <DeleteDialog :open="openDeleteDialog" :title="t('clear_history_dialog_title')"
        :text="t('clear_history_dialog_text')" @confirm="clearHistoryFromDialog" @cancel="openDeleteDialog = false" />
    </q-btn>

    <!-- <SettingsDialog class="settings-btn" /> -->
  </div>
</template>

<script setup lang="ts">
import { toRefs, computed, ref, onMounted } from 'vue'
import { useConversation } from '@/components/composables/use-conversation'
import QuestionCard from '@/components/QuestionCard.vue'
import AnswerCard from '@/components/AnswerCard.vue'
import Sources from '@/components/Sources.vue'
import { useUI } from '@/components/composables/use-ui'
import { useI18n } from 'vue-i18n'
import trashIcon from '@/assets/icons/trash.svg'
import DeleteDialog from '@/components/DeleteDialog.vue'
import SettingsDialog from '@/components/SettingsDialog.vue'
import UserInput from '@/components/UserInput.vue'
import { watch } from 'vue'
import type { FilterConfig } from '@/models'
import { useSettings } from '@/components/composables/use-settings'
import Filters from '@/components/Filters.vue'

const { t } = useI18n()

const openDeleteDialog = ref(false)

const props = defineProps<{
  id: string
}>()

const { id } = toRefs(props)

const scrollAreaRef = ref<HTMLElement>()
let bottomOffset = 0
const {
  currentData,
  currentConversation,
  errorState,
  loadingQuestion,
  sendQuestion,
  isNew,
  clearHistory,
  logFeedback
} = useConversation(id)

async function clearHistoryFromDialog() {
  await clearHistory()
  openDeleteDialog.value = false
}

const { setup } = useUI()
watch(id, scrollToBottom)
function scrollToBottom() {
  setTimeout(() => {
    if (scrollAreaRef.value) {
      scrollAreaRef.value.scrollTop = scrollAreaRef.value.scrollHeight
      bottomOffset = scrollAreaRef.value.scrollTop - scrollAreaRef.value.scrollHeight
    }
  }, 200) //Need time > 100 he scroll size is calculated using a QResizeObserver, and it has a default debounce of 100ms, so any delay over 100ms should be good.
}

function handleSourceExpanded(index: number, newVal: boolean) {
  if (
    currentConversation.value?.data.length &&
    index === currentConversation.value?.data.length - 1 &&
    newVal
  ) {
    scrollToBottom()
  }
}

const inputPlaceholder = computed(() => {
  return setup.value.questionPlaceholder || t('questionPlaceholder')
})

function resizeScrollArea() {
  if (!scrollAreaRef.value) return
  const userInputArea = document.getElementById('user-query-container')
  const wasAtBottom =
    scrollAreaRef.value.scrollTop - scrollAreaRef.value.scrollHeight === bottomOffset
  if (!scrollAreaRef.value || !userInputArea) return
  const textareaHeight = userInputArea.offsetHeight
  scrollAreaRef.value.style.height = 'auto'
  if (
    window.innerWidth <= 500 ||
    (screen.orientation.type.indexOf('landscape') >= 0 &&
      window.innerWidth <= 1000 &&
      window.innerHeight <= 500)
  ) {
    scrollAreaRef.value.style.height = `calc(100% - 40px - ${textareaHeight}px)`
  } else {
    scrollAreaRef.value.style.height = `calc(100% - 60px - ${textareaHeight}px)`
  }
  if (wasAtBottom) {
    scrollToBottom()
  }
}
onMounted(() => {
  resizeScrollArea()
  scrollToBottom()
})
</script>

<style scoped>
.content-container {
  /* margin-top: 22px; */
  height: 100%;
  max-height: 95%;
  width: 100%;
  justify-content: end;
}

/* @media screen and (orientation: landscape) and (max-height: 500px) and (max-width: 1000px) {
  .content-container {
    max-height: 73vh;
  }
} */

.footer-section {
  width: 100%;
  margin-top: 5px;
}

.scroll-area {
  max-height: calc(100% - 100px);
  margin-bottom: 10px;
  margin-top: 0px;
  width: 100%;
  overflow-y: scroll;
  max-height: 100%;
}

.filter-text {
  font-style: normal;
  font-weight: 400;
  font-size: 13px;
  line-height: 20px;
  color: #666666;
}

.doc-info {
  font-size: 11px;
}

.history {
  display: flex;
  gap: 16px;
  flex-direction: column;
  margin-bottom: 16px;
}

.history:first-child {
  padding-top: 0px !important;
}

.history:first-child {
  border-top: none;
}
</style>
