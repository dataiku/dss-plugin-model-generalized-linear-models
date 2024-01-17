<template>
  <div class="items-center q-gutter-y-md empty-state">
    <q-icon :name="logoName" size="117px" class="logo-icon"></q-icon>
    <div class="dku-grand-title-sb" style="color: #666666; text-align: center">
      {{ setup.title }}
    </div>
    <div class="dku-medium-title" style="text-align: center; color: #666666">
      {{ setup.subtitle }}
    </div>
    <UserInput
      :input-placeholder="inputPlaceholder"
      :value="currentData.query"
      :loading="loadingQuestion"
      @send="sendQuestion"
      @enterkey="sendQuestion"
      @update:value="(value) => (currentData.query = value)"
    />
    <div class="title_with_lines">{{ $t('examples') }}</div>
    <div class="row no-wrap q-gutter-x-md examples">
      <InfoCard
        v-for="text in setup.examples"
        :text="text"
        style="cursor: pointer"
        @click="currentData.query = text"
      />
    </div>

    <!-- <SettingsDialog class="settings-btn-empty-state" /> -->
  </div>
</template>
<script lang="ts" setup>
import InfoCard from '@/components/InfoCard.vue'
import logoWithBackground from '@/assets/icons/logo-with-background.svg'
import { useUI } from '@/components/composables/use-ui'
import { useConversation } from '@/components/composables/use-conversation'
import { toRefs, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import UserInput from '@/components/UserInput.vue'
import SettingsDialog from '@/components/SettingsDialog.vue'
const props = defineProps<{
  id: string | null
}>()

const { t } = useI18n()

const { id } = toRefs(props)

const { currentData, sendQuestion, loadingQuestion } = useConversation(id)
const { setup } = useUI()
const logoName = `img:${logoWithBackground}`
const emits = defineEmits<{
  (e: 'example-clicked', text: string): void
}>()

const inputPlaceholder = computed(() => {
  return setup.value.questionPlaceholder || t('questionPlaceholder')
})
</script>

<style scoped lang="scss">
.title_with_lines {
  line-height: 20px;
  text-align: center;
  color: var(--brand);
  font-size: 13px;
  margin-bottom: 19px;
  margin-top: 36px;
}
.title_with_lines {
  display: inline-block;
  position: relative;
}
.title_with_lines:before,
.title_with_lines:after {
  content: '';
  position: absolute;
  overflow: hidden;
  height: 10px;
  border-bottom: 1px solid var(--brand);
  top: 0;
  width: 400px;
}
.title_with_lines:before {
  right: 100%;
  margin-right: 15px;
}
.title_with_lines:after {
  left: 100%;
  margin-left: 15px;
}
.empty-state {
  width: 800px;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: scroll;
  overflow-x: hidden;
  margin-top: 50px;
}

.settings-btn-empty-state {
  top: 6px;
  left: 190px;
  cursor: pointer;
  z-index: 1;
  position: absolute;
  font-family: SourceSansPro;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 142.857% */
}

@media screen and (orientation: landscape) and (max-height: 500px) and (max-width: 1000px),
  (max-width: 767px) {
  /* Styles for phone screens */
  .empty-state {
    width: 100% !important;
    margin-top: 25px;
    margin-bottom: 25px;
  }
  .examples {
    display: flex; /* Enable Flexbox */
    flex-wrap: wrap;
    justify-content: space-between; /* Spread the items equally apart */
    gap: 10px;
    justify-content: center;
    margin-left: 0px;
    max-width: 100%;
  }
  .info-card {
    max-width: 90%;
    margin-left: 0px;
  }
  .logo-icon {
    font-size: 100px !important;
  }
}
</style>
