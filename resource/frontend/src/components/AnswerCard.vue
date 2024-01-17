<template>
  <div class="answer-card q-pa-sm">
    <div class="answer-section column">
      <div class="row no-wrap q-gutter-x-sm">
        <q-icon :name="iconName" size="sm"></q-icon>
        <div class="answer-content">
          <span class="blinking-cursor" v-if="!answer"></span>
          <div v-else>
            <div v-for="block in answerBlocks">
              <span class="answer-text" v-md="block.value" v-if="block.type == 'markdown'" :style="answerStyle"></span>
              <code-display v-else :value="block.value" />
            </div>
          </div>
          <slot></slot>
        </div>
      </div>

      <div class="feedback-buttons self-end" v-if="answer">
        <q-icon class="feedback-icon" @click="copyAnswer">
          <copy-icon />
        </q-icon>
        <q-icon class="feedback-icon" v-if="!isNegativeFeedback">
          <thumbs-up :active="isPositiveFeedback" />
          <feedback-proxy-popup
            v-if="!submitted"
            :feedback-value="FeedbackValue.POSITIVE"
            :feedback-options="feedbackOptionsPositive"
            :submit-on-hide="true"
            @save="(value) => submitFeedback(value)"
            />
          </q-icon>
          <q-icon class="feedback-icon" v-if="!isPositiveFeedback">
            <thumbs-down :active="isNegativeFeedback" />
            <feedback-proxy-popup
            v-if="!submitted"
            :feedback-value="FeedbackValue.NEGATIVE"
            :feedback-options="feedbackOptionsNegative"
            :submit-on-hide="false"
            @save="(value) => submitFeedback(value)"
          />
        </q-icon>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import AnswerIcon from '@/assets/icons/answer-icon.svg'
import { useClipboard } from '@/components/composables/use-clipboard'
import { FeedbackValue, type Feedback } from '@/models'
import { computed, ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import CopyIcon from './icons/CopyIcon.vue'
import ThumbsDown from './icons/ThumbsDown.vue'
import ThumbsUp from './icons/ThumbsUp.vue'
import FeedbackProxyPopup from './FeedbackProxyPopup.vue'
import { isEqual } from 'lodash'
import CodeDisplay from './CodeDisplay.vue'

const { isCopySupported, copyToClipboard } = useClipboard()

const { t } = useI18n()

const props = defineProps<{
  answer: string
  feedback: Feedback | null
  typingEffectOn: boolean
  errorState: boolean
  feedbackOptionsNegative: string[]
  feedbackOptionsPositive: string[]
}>()

const emits = defineEmits<{
  (e: 'update:feedback', feedback: Feedback): void
}>()

const iconName = `img:${AnswerIcon}`

const isNegativeFeedback = computed(() => {
  return props.feedback && props.feedback.value === FeedbackValue.NEGATIVE ? true : false
})

const isPositiveFeedback = computed(() => {
  return props.feedback && props.feedback.value === FeedbackValue.POSITIVE ? true : false
})

const submitted = computed(() => {
  return isNegativeFeedback.value || isPositiveFeedback.value
})

const answerStyle = computed(() => {
  return {
    color: props.answer == t('error_answer') ? 'red' : ''
  }
})

let timeout: ReturnType<typeof setTimeout> = 0

const answerBlocks = ref<AnswerBlock[]>([])

const copied = ref<boolean>(false)

async function copyAnswer() {
  if (!isCopySupported.value) return
  const isCopied = await copyToClipboard(props.answer)
  if (!isCopied) return
  copied.value = true
}

function submitFeedback(feedback: Feedback) {
  if (!isEqual(feedback, props.feedback)) {
    emits('update:feedback', feedback)
  }
}

onMounted(() => {
  timeout = 0
  buildAnswer(props.answer)
})

onBeforeUnmount(() => {
  clearTimeout(timeout)
})

function buildAnswer(answer: string) {
  answerBlocks.value = parseString(answer)
}

watch(
  () => props.answer,
  (newAnswer, oldAnswer) => {
    buildAnswer(newAnswer)
  }
)

interface AnswerBlock {
  type: 'markdown' | 'code'
  value: string
}

function parseString(inputString: string): AnswerBlock[] {
  const codePattern = /```(\w+[\s\S]*?)```/gm
  const codeBlocks = []

  let codeMatch
  while ((codeMatch = codePattern.exec(inputString)) !== null) {
    codeBlocks.push({
      value: codeMatch[1].trim(),
      start: codeMatch.index,
      end: codeMatch.index + codeMatch[0].length
    })
  }

  if (codeBlocks.length === 0) {
    return [{ type: 'markdown', value: inputString.trim() }]
  }

  const blocks: AnswerBlock[] = []
  const sortedCodeBlocks = codeBlocks.slice().sort((a, b) => a.start - b.start)

  sortedCodeBlocks.forEach((entry, i) => {
    const start = entry.start
    const end = entry.end
    const value = entry.value

    const prevEndIndex = i > 0 ? sortedCodeBlocks[i - 1].end : 0
    const markdownBeforeCode = inputString.slice(prevEndIndex, start).trim()

    if (markdownBeforeCode.length > 0) {
      blocks.push({ type: 'markdown', value: markdownBeforeCode })
    }

    blocks.push({ type: 'code', value: value })
  })

  const lastEndIndex = sortedCodeBlocks[sortedCodeBlocks.length - 1].end
  const markdownAfterLastCode = inputString.slice(lastEndIndex).trim()

  if (markdownAfterLastCode.length > 0) {
    blocks.push({ type: 'markdown', value: markdownAfterLastCode })
  }

  return blocks
}
</script>

<style scoped>
.answer-card {
  max-width: 95%;
  width: auto;
  background: #f5f5f5;
  /* background: var(--bg-brand); */
  border-radius: 6px;
  padding: 8px;
  align-self: flex-start;
}
.answer-section {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 100%;
}
.answer-content {
  flex-grow: 1;
  word-wrap: break-word;
  overflow: hidden; /* Prevents overflowing */
}

.feedback-buttons {
  display: flex;
  color: #6666;
}
.feedback-icon.active {
  color: var(--brand);
}
.feedback-icon,
.copy-icon {
  margin-right: 8px;
  cursor: pointer;
  align-self: flex-start;
}

.answer-text {
  font-style: normal;
  font-weight: 400;
  font-size: 13px;
  line-height: 20px;
  max-width: 90%;
  color: #444;
  margin-bottom: 6px;
}
.blinking-cursor {
  display: inline-block;
  width: 6px;
  height: 20px;
  background-color: #444444;
  animation: blink 0.8s infinite;
}

@keyframes blink {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

.answer-text a {
  color: var(--brand);
  text-decoration: none;
  transition: color 0.3s ease;
}

.answer-text a:hover {
  color: var(--brand);
  text-decoration: underline;
}
@media (max-width: 767px) {
  .answer-card {
    max-width: 90%;
  }
}
</style>
