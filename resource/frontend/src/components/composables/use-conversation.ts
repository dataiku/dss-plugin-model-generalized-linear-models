import { ServerApi } from '@/api/server_api'
import { ResponseStatus, type QuestionData, type Feedback } from '@/models'
import type { Conversation } from '@/models/conversation'
import { ref, computed, watch } from 'vue'
import type { Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Notify } from 'quasar'
import { nanoid } from 'nanoid'
import { useRouter } from 'vue-router'
import { useConversations } from './use-conversations'
import { createNotification } from '@/common/utils'
import { useSettings } from './use-settings'

const initData: QuestionData = {
  id: '',
  query: '',
  answer: '',
  filters: {},
  sources: [],
  feedback: null
}
const currentData = ref<QuestionData>({ ...initData })
const currentConversation = ref<Conversation | null>(null)
const loadingQuestion = ref<boolean>(false)

export function useConversation(id: Ref<string | null>) {
  const { t } = useI18n()

  const { getUserConversations, conversations } = useConversations()
  const router = useRouter()

  const loading = ref<boolean>(false)
  const error = ref<any>(null)

  const errorState = ref<boolean>(false)

  const { filtersSelections, knowledgeBankSelection } = useSettings();

  const queryFilters = computed(() => {
    
    const result: Record<string, any[]> = {};
    if(knowledgeBankSelection.value){
      for (const key in filtersSelections.value) {
        if (filtersSelections.value[key] && filtersSelections.value[key].length > 0) {
          result[key] = filtersSelections.value[key]
        }
      }
    }
    return Object.keys(result).length > 0 ? result : null;
  });

  function createTmpId() {
    return `_${nanoid()}`
  }

  function handleErrorResponse(response: any) {
    errorState.value = true
    const errorAnswerTranslated = t('error_answer')
    const errorMsgTranslated = t('error_message')
    currentData.value = {
      ...currentData.value,
      answer: errorAnswerTranslated
    }
    if (currentConversation.value?.data.length && currentConversation.value?.data.length > 0) {
      currentConversation.value.data[currentConversation.value?.data.length - 1] =
        currentData.value
    }

    currentData.value = { ...initData }
    if (response.status && response.status == ResponseStatus.KO) {
      createNotification('negative', response.message)
    } else {
      createNotification('negative', errorMsgTranslated)
    }
  }

  const isNew = computed(() => {
    return id.value == null || id.value.startsWith('_')
  })

  async function getConversation() {
    // only get conversation history when not new
    if (isNew.value) return

    loading.value = true

    try {
      if (!id.value) return
      const response = await ServerApi.getConversation(id.value)
      if (response && response.data) {
        currentConversation.value = response.data
      }
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  async function reset() {
    loading.value = false
    error.value = null
    currentData.value = { ...initData }
    currentConversation.value = null
    await getConversation()
  }

  async function sendQuestion() {
    if (!currentData.value.query) return

    loadingQuestion.value = true

    currentData.value = {
      ...initData,
      query: currentData.value.query,
      filters: queryFilters.value
    }

    if (isNew.value) {
      router.push({ path: `/conversation/${createTmpId()}` })
    }

    try {
      const result = await fetchAnswer()
      if (isNew.value && result) {
        if (currentConversation.value) {
          currentConversation.value.name = result.conversationName
          conversations.value = conversations.value.map((conv) => {
            if (conv.id === result.conversationId)
              return {
                ...conv,
                name: result.conversationName
              }
            return conv
          })
        }
      }
    } catch (e) {
      handleErrorResponse(e)
    } finally {
      loadingQuestion.value = false
    }
  }

  async function fetchAnswer() {
    if (isNew.value) {
      currentConversation.value = startTmpConv()
    }

    currentConversation.value?.data.push(currentData.value)

    const question = currentData.value.query

    const response = await ServerApi.getAnswer({
      conversation_id: id.value,
      query: currentData.value.query,
      filters: queryFilters.value,
      knowledge_bank_id: knowledgeBankSelection.value ?? ''
    })

    if (response.status == ResponseStatus.OK) {
      currentData.value = {
        ...currentData.value,
        sources: response.data.sources,
        answer: response.data.answer,
        filters: response.data.filters,
        id: String(response.data.record_id)
      }
      const convInfos = response.data.conversation_infos

      if (isNew.value) {
        await getUserConversations()
        await router.push({ path: `/conversation/${convInfos.id}` })
        // trigger a list conv refresh
      }

      if (currentConversation.value?.data.length && currentConversation.value?.data.length > 0) {
        currentConversation.value.data[currentConversation.value?.data.length - 1] =
          currentData.value
      }

      currentData.value = { ...initData }

      return {
        conversationId: convInfos.id,
        conversationName: convInfos.name,
        query: question,
        answer: response.data.answer
      }
    }
  }

  function startTmpConv() {
    const conversation: Conversation = {
      auth_identifier: '',
      id: createTmpId(),
      data: [],
      name: '',
      timestamp: 0
    }
    return conversation
  }

  async function clearHistory() {
    try {
      if (!id.value || isNew.value) return
      await ServerApi.clearHistory(id.value)
      if (currentConversation.value?.data) {
        currentConversation.value.data = []
      }
    } catch (e) {
      createNotification('negative', t('error_message'))
    }
  }

  async function logFeedback(record_id: string | number, item: QuestionData, feedback: Feedback) {
    if (!id.value || isNew.value) return
    try {
      item.feedback = feedback
      await ServerApi.logFeedback(id.value, record_id, item)

      if (currentConversation.value?.data) {
        currentConversation.value.data = currentConversation.value.data.map((val, index) => {
          if (index === record_id) {
            const result = { ...val, feedback: feedback }
            return result
          }
          return val
        })
      }
      createNotification('positive', t('feedback_succes_message'))
    } catch (e) {
      createNotification('negative', t('error_message'))
    }
  }

  watch(
    () => id.value,
    () => {
      if (!(id.value == null || id.value.startsWith('_'))) reset()
    },
    { immediate: true }
  )

  return {
    currentData,
    currentConversation,
    sendQuestion,
    loadingQuestion,
    errorState,
    reset,
    isNew,
    clearHistory,
    logFeedback
  }
}
