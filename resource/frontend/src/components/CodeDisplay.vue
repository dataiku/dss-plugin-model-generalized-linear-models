<template>
  <div class="code-wrapper">
    <div class="header row justify-between items-center">
      <div>{{ codeComponents.identifier }}</div>
      <div class="row items-center q-gutter-x-xs copy" @click="copyCode">
        <q-icon>
          <copy-icon color="white" />
        </q-icon>
        <div class="copy-text">{{ t('copy_code') }}</div>
      </div>
    </div>
    <pre class="code-container">
        <code v-html="codeComponents.code"></code>
    </pre>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Prism from 'prismjs'
import CopyIcon from './icons/CopyIcon.vue'
import { useClipboard } from '@/components/composables/use-clipboard'

interface CodeCompenents {
  identifier: string
  code: string
}

const { t } = useI18n()

const props = defineProps<{
  value: string
}>()

const { isCopySupported, copyToClipboard } = useClipboard()

const copied = ref<boolean>(false)

const defaultIdentifier = t('unknown')

function extractCodeSnippet(input: string): CodeCompenents {
  const codeSnippetPattern = /(?:^|\n)([^\n]+)([\s\S]*)/

  const match = input.match(codeSnippetPattern)

  if (match && match.length === 3) {
    const [, identifier, content] = match
    return { identifier, code: content }
  }

  return { identifier: defaultIdentifier, code: '' }
}

const codeComponents = computed(() => {
  if (!props.value) return { identifier: defaultIdentifier, code: '' } as CodeCompenents
  const { identifier, code } = extractCodeSnippet(props.value)
  let highlightedCode = code
  try {
    const grammar = Prism.languages[identifier]
    if (grammar) highlightedCode = Prism.highlight(code, grammar, identifier)
    else highlightedCode = Prism.highlight(code, Prism.languages['javascript'], 'javascript')
  } catch (e) {
    //
  }
  return { identifier, code: highlightedCode }
})

async function copyCode() {
  if (!isCopySupported.value) return
  const isCopied = await copyToClipboard(props.value)
  if (!isCopied) return
  copied.value = true
}
</script>

<style scoped lang="scss">
.code-wrapper {
  background-color: #282c34;
  border-radius: 4px;
  color: #f8f8f8;
  font-family: 'Courier New', Courier, monospace;
  word-wrap: break-word;
  overflow-x: hidden;
  max-width: 100%;
}


.code-container {
  padding: 8px;
  word-wrap: break-word;
  overflow-x: auto;
  white-space: pre-wrap;
  max-width: 100%;
}

.header {
  padding: 8px;
  width: 100%;
  background-color: #202123;
}
.copy {
  cursor: pointer;
}
.copy-text {
  color: var(--greyscale-grey-lighten-4, #999);
  /* .dds-caption-400 */
  font-family: SourceSansPro;
  font-size: 12px;
  font-style: normal;
  font-weight: 400;
  line-height: 15px;
}
</style>
