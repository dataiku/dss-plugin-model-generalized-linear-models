import { computed } from 'vue'
import { Notify } from 'quasar'
import { useI18n } from 'vue-i18n'
import { createNotification } from '@/common/utils'

type Message = {
  success?: string
  fail?: string
}

export function useClipboard() {
  const { t } = useI18n()

  const isCopySupported = computed(() => {
    return !!navigator?.clipboard?.writeText
  })

  const isPasteSupported = computed(() => {
    return !!navigator?.clipboard?.readText
  })

  async function copyToClipboard(value: any, message?: Message): Promise<boolean> {
    try {
      const valueString = typeof value === 'string' ? value : JSON.stringify(value)
      await navigator?.clipboard?.writeText(valueString)

      createNotification('positive', message?.success ?? t('copy_raw_value_success'))
      return true
    } catch (err: any) {
      createNotification('negative', message?.fail ?? t('copy_raw_value_fail'))

      return false
    }
  }

  return { isCopySupported, isPasteSupported, copyToClipboard }
}
