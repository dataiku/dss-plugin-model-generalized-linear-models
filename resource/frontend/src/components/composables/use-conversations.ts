import type { ConversationInfo } from '@/models/conversation'
import { ref, onMounted } from 'vue'
import { ServerApi } from '@/api/server_api'
import { Notify } from 'quasar'
import { useI18n } from 'vue-i18n'
import { createNotification } from '@/common/utils'

const conversations = ref<ConversationInfo[]>([])

export function useConversations() {
  const loading = ref<boolean>(false)
  const error = ref<any>(null)
  const { t } = useI18n()

  async function getUserConversations() {
    loading.value = true
    try {
      const response = await ServerApi.getUserConversations()
      if (response && response.data) {
        let convs = response.data
        convs.sort((a, b) => b.timestamp - a.timestamp)
        conversations.value = convs
      }
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  async function deleteConversation(id: string) {
    try {
      if (conversations.value.findIndex((item) => item.id === id) === -1) return
      await ServerApi.deleteConversation(id)
      conversations.value = conversations.value.filter((item) => item.id === id)
      createNotification('positive', t('delete_item_success'))
    } catch (e) {
      createNotification('negative', t('error_message'))
    }
  }

  async function deleteAllConversations() {
    try {
      if (conversations.value.length === 0) return
      await ServerApi.deleteAllConversations()
      conversations.value = []
      createNotification('positive', t('delete_items_success'))
    } catch (e) {
      createNotification('negative', t('error_message'))
    }
  }

  onMounted(async () => {
    await getUserConversations()
  })

  return {
    conversations,
    loading,
    error,
    getUserConversations,
    deleteConversation,
    deleteAllConversations
  }
}
