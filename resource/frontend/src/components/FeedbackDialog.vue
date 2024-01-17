<template>
  <q-dialog persistent :model-value="open">
    <q-card class="q-dialog-plugin">
      <q-card-section>
        <div class="row items-center no-wrap bs-title dku-grand-title">
          <div style="flex-grow: 1; color: " class="row items-center">
            <q-icon
              :name="
                feedbackValue == FeedbackValue.POSITIVE ? mdiThumbUpOutline : mdiThumbDownOutline
              "
              style="margin-right: 4px"
            />
            {{ title }}
          </div>
          <BsButton icon="close" @click="emits('cancel')" dense v-close-popup> </BsButton>
        </div>
      </q-card-section>
      <q-separator />
      <q-card-section>
        <BsCheckbox
          v-for="(option, index) in feedbackOptions"
          :key="index"
          :label="option"
          v-model="selectedFeedback[index]"
        ></BsCheckbox>
        <div class="q-mt-md">
          <textarea
            :placeholder="placeholder"
            v-model="feedbackMessage"
            outlined
            class="comment-input"
            maxlength="500"
          ></textarea>
        </div>
      </q-card-section>
      <q-card-section>
        <!-- buttons example -->
        <q-card-actions align="right">
          <BsButton
            class="bs-font-medium-2-normal"
            unelevated
            dense
            textColor="primary"
            @click="onSubmit"
          >
            {{ t('submit') }}</BsButton
          >
        </q-card-actions>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>
<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { FeedbackValue, type Feedback } from '@/models'
import { useI18n } from 'vue-i18n'
import { mdiThumbDownOutline, mdiThumbUpOutline } from '@quasar/extras/mdi-v6'

const props = defineProps<{
  open: boolean
  feedbackValue: FeedbackValue
  feedbackOptionsNegative: string[]
  feedbackOptionsPositive: string[]
}>()

const { t } = useI18n()

const title = computed(() => {
  return props.feedbackValue == FeedbackValue.NEGATIVE
    ? t('feedback_title_negative')
    : t('feedback_title_positive')
})

const placeholder = computed(() => {
  return props.feedbackValue == FeedbackValue.NEGATIVE
    ? t('feedback_dialog_placeholder_negative')
    : t('feedback_dialog_placeholder_positive')
})

const feedbackOptions = ref<string[]>([])

const selectedFeedback = ref<boolean[]>([])

watch(
  () => props.feedbackValue,
  (newVal, oldVal) => {
    if (newVal == FeedbackValue.POSITIVE) {
      feedbackOptions.value = props.feedbackOptionsPositive
      selectedFeedback.value = props.feedbackOptionsPositive.map((el) => false)
    } else {
      feedbackOptions.value = props.feedbackOptionsNegative
      selectedFeedback.value = props.feedbackOptionsNegative.map((el) => false)
    }
  },
  { immediate: true }
)

const feedbackMessage = ref('')

const emits = defineEmits<{
  (e: 'cancel'): void
  (e: 'confirm', feedback: Feedback): void
}>()

function onSubmit() {
  const choices: string[] = []

  selectedFeedback.value.forEach((item, index) => {
    if (item && index < feedbackOptions.value.length && feedbackOptions.value[index]) {
      choices.push(feedbackOptions.value[index])
    }
  })
  const feedback: Feedback = {
    value: props.feedbackValue,
    message: feedbackMessage.value,
    choice: choices
  }

  emits('confirm', feedback)
}
</script>

<style lang="scss" scoped>
.bs-title {
  color: var(--greyscale-grey-lighten-1, #333);
  gap: 8px;
}
.comment-input {
  padding: 8px 12px;
  min-height: 100px;
  max-height: 300px;
  min-width: 100%;
  max-width: 100%;
  border: 1px solid #c8c8c8;
  border-radius: 4px;
}
.comment-input:focus {
  outline: none !important;
  border: 1px solid var(--brand);
}
@media (max-width: 500px) {
  /* Styles for phone screens */
  .bs-title {
    font-size: 16px;
  }
  :deep(.bs-title .q-btn .q-icon) {
    font-size: 20px;
  }
  .comment-input {
    max-height: 100px;
  }
}
</style>
