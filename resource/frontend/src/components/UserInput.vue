<template>
  <div class="user-input-wrapper" style="width: 100%">
    <textarea
      ref="textAreaAreaRef"
      v-model="internalValue"
      res
      class="query-input"
      :placeholder="inputPlaceholder"
      @keydown="(e: KeyboardEvent) => handleKey(e)"
      @focus="handleFocus(true)"
      @blur="handleFocus(false)"
      :disabled="props.loading"
    >
    </textarea>
    <q-icon
      v-if="!loading"
      name="send"
      class="cursor-pointer send-icon"
      @click="emits('send')"
      size="xs"
      :style="activeStyle"
    />
    <div v-else style="left: -30px; width: 10px; position: relative; top: 8px; color: var(--brand)">
      <q-spinner size="sm" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSync } from '@/components/composables/use-sync'
import { watch } from 'vue'
const props = defineProps<{
  value: string
  loading: boolean
  inputPlaceholder: string
}>()

const emits = defineEmits(['send', 'enterkey', 'update:value', 'sizeChange'])

const internalValue = useSync(props, 'value', emits)
const focused = ref(false)
const textAreaAreaRef = ref<InstanceType<typeof HTMLElement> | null>(null)
function handleKey(e: KeyboardEvent) {
  adjustTextareaHeight()

  if (e.key === 'Enter') {
    e.stopPropagation()
    if (!e.shiftKey) {
      // Prevent the default Enter key behavior and emit the 'enterkey' event
      e.preventDefault()
      emits('enterkey')
    }
  }
}
watch(internalValue, () => {
    setTimeout(() => {
      adjustTextareaHeight()
    }, 0)
})
function handleFocus(isFocused: boolean) {
  focused.value = isFocused
}
function adjustTextareaHeight() {
  const textareaElement = textAreaAreaRef.value
  if (!textareaElement) return
  const maxHeight = 150
  if(internalValue.value === ""){
    textareaElement.style.height = '40px';
  }else{
    if (textareaElement.scrollHeight > maxHeight) {
      textareaElement.style.height = `${maxHeight}px` // Set to max height if content exceeds it
    } else {
      textareaElement.style.height = `${Math.max(textareaElement.scrollHeight, textareaElement.offsetHeight)}px` // Expand height to fit content
    }
    if (textareaElement.scrollHeight <= 40) {
      textareaElement.style.overflowY = 'hidden'
    } else {
      textareaElement.style.overflowY = 'auto'
    }
  }
  emits('sizeChange', textareaElement.style.height)
}

const activeStyle = computed(() => {
  if (props.loading) {
    return {
      color: '#CCCCCC',
      cursor: 'wait !important'
    }
  } else {
    if (internalValue.value) {
      return {
        color: 'var(--brand)',
        cursor: 'pointer'
      }
    } else {
      return {
        color: '#CCCCCC',
        cursor: 'not-allowed !important'
      }
    }
  }
})
</script>

<style scoped lang="scss">
.user-input-wrapper {
  display: flex;
  flex-direction: row;
}
.query-input {
  padding: 8px 12px;
  height: 40px;
  min-height: 40px;
  max-height: 100px;
  font-size: 16px;
  min-width: calc(100% - 1px);
  max-width: calc(100% - 1px);
  border: 1px solid #c8c8c8;
  border-radius: 4px;
  resize: none;
  overflow-y: hidden;
}
.query-input:focus {
  outline: none !important;
  border: 1px solid var(--brand);
}
textarea:disabled {
  background: var(--greyscale-grey-lighten-8, #f2f2f2);
}
.user-input-wrapper {
  position: relative;
  width: 100%;
}
.send-icon,
.spinner-wrapper {
  position: absolute;
  right: 8px;
  top: 8px;
}

.send-icon {
  margin-bottom: 4px;
  transform: rotate(-38.48deg);
  padding-top: 8px;
  top: 2px; 
}
</style>
