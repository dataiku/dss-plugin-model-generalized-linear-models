<template>
  <q-popup-proxy :offset="[10, 10]" style="min-width: 270px" v-model="open" @hide="hideOrSubmit">
    <q-card class="card-container">
      <q-card-section>
        <div class="row items-center q-gutter-x-xs no-wrap">
          <q-icon size="16px">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
            >
              <path
                d="M1.00073 7.96559C1.00073 4.12594 4.13789 1.01953 8.00037 1.01953C11.8628 1.01953 15 4.12594 15 7.96559C15 11.8052 11.8628 14.9117 8.00037 14.9117C6.89513 14.9117 5.85195 14.6539 4.92308 14.201L2.11158 14.9488C2.11148 14.9488 2.11139 14.9488 2.1113 14.9488C1.46125 15.1231 0.853473 14.5326 1.03139 13.8733L1.03141 13.8732L1.77081 11.1351C1.27925 10.1847 1.00073 9.10709 1.00073 7.96559ZM8.00037 1.89449C4.61434 1.89449 1.87569 4.61591 1.87569 7.96559C1.87569 9.01867 2.1466 10.008 2.62158 10.8711C2.67616 10.9703 2.69017 11.0867 2.66066 11.1961L1.87613 14.1012C1.87611 14.1013 1.87609 14.1014 1.87607 14.1014C1.87626 14.1017 1.87648 14.1019 1.87674 14.1022C1.87862 14.104 1.88017 14.1046 1.88023 14.1046L1.88019 14.1046L1.88011 14.1045C1.88013 14.1045 1.88157 14.1046 1.88478 14.1037L1.88574 14.1035L4.85864 13.3128C4.96379 13.2848 5.07559 13.297 5.17221 13.3471C6.01953 13.7857 6.97937 14.0367 8.00037 14.0367C11.3864 14.0367 14.125 11.3153 14.125 7.96559C14.125 4.61591 11.3864 1.89449 8.00037 1.89449ZM1.88011 14.1045C1.88001 14.1045 1.88002 14.1045 1.8801 14.1045L1.88011 14.1045Z"
                fill="black"
              />
            </svg>
          </q-icon>
          <div class="dds-default-text-400">{{ title }}</div>
          <q-icon size="16px" style="cursor: pointer" @click="closePopup">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
            >
              <path
                d="M2.58859 2.71569L2.64645 2.64645C2.82001 2.47288 3.08944 2.4536 3.28431 2.58859L3.35355 2.64645L8 7.293L12.6464 2.64645C12.8417 2.45118 13.1583 2.45118 13.3536 2.64645C13.5488 2.84171 13.5488 3.15829 13.3536 3.35355L8.707 8L13.3536 12.6464C13.5271 12.82 13.5464 13.0894 13.4114 13.2843L13.3536 13.3536C13.18 13.5271 12.9106 13.5464 12.7157 13.4114L12.6464 13.3536L8 8.707L3.35355 13.3536C3.15829 13.5488 2.84171 13.5488 2.64645 13.3536C2.45118 13.1583 2.45118 12.8417 2.64645 12.6464L7.293 8L2.64645 3.35355C2.47288 3.17999 2.4536 2.91056 2.58859 2.71569L2.64645 2.64645L2.58859 2.71569Z"
                fill="#333E48"
              />
            </svg>
          </q-icon>
        </div>
      </q-card-section>
      <q-card-section>
        <div class="caption-text">{{ caption }}</div>
        <div class="column">
          <q-chip
            class="chip"
            v-model:selected="localChoiceSelection[option]"
            :class="{ active: localChoiceSelection[option] }"
            v-for="(option, index) in feedbackOptions"
            square
            clickable
            :key="index"
          >
            {{ option }}
          </q-chip>
        </div>
      </q-card-section>
      <q-card-section>
        <UserInput
          :value="localFeedbackMessage"
          :inputPlaceholder="t('feedback_input_placeholder')"
          :loading="loading"
          @send="emitSave"
          @enterkey="emitSave"
          @update:value="(value) => (localFeedbackMessage = value)"
        />
      </q-card-section>
    </q-card>
  </q-popup-proxy>
</template>

<script setup lang="ts">
import { FeedbackValue, type Feedback } from '@/models'
import { ref, computed } from 'vue'
import UserInput from './UserInput.vue'
import { useI18n } from 'vue-i18n'

const open = ref(false)

const explicitClose = ref(false)

const { t } = useI18n()

const props = defineProps<{
  feedbackValue: FeedbackValue
  feedbackOptions: string[]
  submitOnHide: boolean
}>()

const localChoiceSelection = ref<Record<string, boolean>>(
  Object.fromEntries(
    props.feedbackOptions.map((item) => {
      return [item, false]
    })
  )
)

const emits = defineEmits<{
  (e: 'save', feedback: Feedback): void
}>()

const localFeedbackMessage = ref<string>('')

const feedback = computed(() => {
  const result: Feedback = {
    value: props.feedbackValue,
    message: localFeedbackMessage.value,
    choice: Object.entries(localChoiceSelection.value)
      .filter((item) => item[1])
      .map((item) => item[0])
  }
  return result
})

const loading = ref(false)

const caption = computed(() => {
  return props.feedbackValue === FeedbackValue.POSITIVE
    ? t('feedback_dialog_placeholder_positive')
    : t('feedback_dialog_placeholder_negative')
})

const title = computed(() => {
  return props.feedbackValue === FeedbackValue.POSITIVE
    ? t('feedback_title_positive')
    : t('feedback_title_negative')
})

function closePopup() {
  explicitClose.value = true
  open.value = false
  if(props.submitOnHide){
    emitSave()
  }
}
function hideOrSubmit(){
  if(props.submitOnHide){
    emitSave();
  }
}
function emitSave() {
  if (!explicitClose.value) {
    emits('save', feedback.value)
  }

  explicitClose.value = false
}
</script>

<style scoped lang="scss">
.card-container {
  border-radius: 4px;
  border: 1px solid var(--gis-turquoise-disabled, #a6d6d4);
  background: var(--White, #fff);
  box-shadow: 0px 3px 8px 0px rgba(0, 0, 0, 0.12);
}

.dds-default-text-400 {
  font-family: SourceSansPro;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 142.857% */
  margin-right: 36px;
}

.caption-text {
  font-family: SourceSansPro;
  font-size: 10px;
  font-style: normal;
  font-weight: 400;
  line-height: 16px; /* 160% */
  color: var(--greyscale-grey-lighten-4, var(--greyscale-grey-lighten-4, #999));
}

.chip {
  margin-left: 0;
  border-radius: 3.726px;
  border: 1px solid var(--light_grey, #eaeff3);
  background-color: #fff;
  font-family: SourceSansPro;
  font-size: 12px;
  font-style: normal;
  font-weight: 400;
  line-height: 15px; /* 125% */
  color: var(--dss-objects-dark-teal-base, #3b7879);
  width: fit-content;

  &.active {
    background-color: rgba(67, 125, 126, 0.07);
    border: 1px solid #629394;
  }
}

:deep(.q-chip__icon) {
  color: #609192 !important;
}
</style>
