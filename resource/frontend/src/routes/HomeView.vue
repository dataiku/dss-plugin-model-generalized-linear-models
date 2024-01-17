<template>
  <BsLayoutDefault ref="layout">
    <BsDrawer>
      <BsButton
        flat
        round
        class="close-side-drawer-btn"
        size="15px"
        @click="closeSideDrawer"
        :icon="mdiArrowLeft"
      >
        <BsTooltip>Close sidebar</BsTooltip>
      </BsButton>
      <q-scroll-area style="height: 100vh; max-width: 100%">
        <div class="q-pa-md">
          <div class="row fit no-wrap items-center q-gutter-x-sm" style="margin-bottom: 10px">
            <span class="all-title">{{ t('all_conversations') }}</span>
          </div>
          <div class="flex row" style="justify-content: space-between; margin-top: 10px">
            <q-btn
              flat
              dense
              color="primary"
              style="padding-left: 0; margin-bottom: 3px"
              @click="newConversation"
              no-caps
              class="new-chat-btn"
              ><q-icon :name="`img:${addSquareIcon}`" size="18px" style="margin-right: 2px"></q-icon
              >{{ t('new_chat') }}
            </q-btn>
            <q-btn
              flat
              dense
              color="primary"
              style="padding-left: 0; margin-bottom: 3px"
              @click="deleteAllOpen = true"
              no-caps
              class="new-chat-btn"
              v-if="conversations.length"
            >
              <q-icon
                :name="`img:${trashIcon}`"
                size="16px"
                style="cursor: pointer"
                @click="deleteAllOpen = true"
              >
              </q-icon>
              {{ t('delete_all_conv_title') }}
              <DeleteDialog
                :open="deleteAllOpen"
                :title="t('delete_all_conv_title')"
                :text="t('delete_all_conv_warning')"
                @cancel="deleteAllOpen = false"
                @confirm="deleteAllItems"
              >
                {{ t('delete_all_conv_message') }}
              </DeleteDialog>
            </q-btn>
          </div>

          <div
            class="column no-wrap justify-center align-center q-gutter-y-sm"
            v-if="!loadingConversations && !errorConversations"
          >
            <ConversationCard
              v-for="(item, index) in conversations"
              :title="item.name"
              :date="item.timestamp"
              :id="item.id"
              :is-selected="isSelected(item.id)"
              @update:conv="(id) => navigateToConv(id)"
              @delete:conv="(id) => deleteItem(id)"
            />
          </div>
          <div v-else-if="errorConversations">
            <div>ERROR</div>
          </div>
          <div v-else>
            <q-spinner color="primary" size="3em"></q-spinner>
          </div>
        </div>
      </q-scroll-area>
    </BsDrawer>
    <BsContent>
      <BsButton
        flat
        round
        class="open-side-drawer-btn"
        size="15px"
        @click="closeSideDrawer"
        :icon="mdiArrowRight"
        v-if="!layout?.drawerOpen"
      >
        <BsTooltip>Open sidebar</BsTooltip>
      </BsButton>
      <BsDocumentation :doc-icon="logoWithBackground"><Documentation></Documentation> </BsDocumentation>
      <div class="absolute-center content-wrapper">
        <div class="column items-center doc-intelligence-content">
          <SettingsDialog class="settings-btn" />
          <RouterView />
        </div>
      </div>
    </BsContent>
  </BsLayoutDefault>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useUI } from '@/components/composables/use-ui'
import { useConversations } from '@/components/composables/use-conversations'
import { useConversation } from '@/components/composables/use-conversation'
import { useRouter } from 'vue-router'
import DeleteDialog from '@/components/DeleteDialog.vue'
import trashIcon from '@/assets/icons/trash.svg'
import addSquareIcon from '@/assets/icons/add_square.svg'
import ConversationCard from '@/components/ConversationCard.vue'
import logoWithBackground from '@/assets/icons/logo-with-background.svg'
import { BsButton, type BsLayoutDefault } from 'quasar-ui-bs'
import { mdiArrowLeft, mdiArrowRight } from '@quasar/extras/mdi-v6'
import { onMounted } from 'vue'
import SettingsDialog from '@/components/SettingsDialog.vue'
import Documentation from '@/components/Documentation.vue'

const router = useRouter()
const id = ref<string | null>(null)

const { reset } = useConversation(id)

const { setup } = useUI()
const { t } = useI18n()

function isSelected(itemId: string) {
  const route = useRoute()
  const converationId = route.params.id
  return itemId === converationId
}

const deleteAllOpen = ref<boolean>(false)

const deleteItemOpen = ref<number | null>(null)
const layout = ref<InstanceType<typeof BsLayoutDefault> | null>(null)

const {
  conversations,
  loading: loadingConversations,
  error: errorConversations,
  deleteConversation,
  deleteAllConversations
} = useConversations()

async function newConversation() {
  await reset()
  await router.push({ path: '/new' })
  closeSideBarForSmallScreen()
}

async function deleteItem(id: string) {
  await deleteConversation(id)
  await router.push({ path: '/new' })
  await reset()
}

async function deleteAllItems() {
  await deleteAllConversations()
  await router.push({ path: '/new' })
  await reset()
  deleteAllOpen.value = false
}
function closeSideBarForSmallScreen() {
  // If we are on a small screen we close the side bar
  // and (orientation: landscape) and (max-height: 500px) and (max-width: 1000px) to match css breakpoints
  if (
    window.innerWidth <= 500 ||
    (screen.orientation.type.indexOf('landscape') >= 0 &&
      window.innerWidth <= 1000 &&
      window.innerHeight <= 500)
  ) {
    closeSideDrawer()
  }
}
function navigateToConv(id: string) {
  router.push({ path: `/conversation/${id}` })
  closeSideBarForSmallScreen()
}
function closeSideDrawer() {
  if (layout.value) {
    layout.value.drawerOpen = !layout.value.drawerOpen
  }
}

onMounted(() => {
  closeSideBarForSmallScreen()
})
</script>
<style lang="scss">
.q-scrollarea__content {
  max-width: 100% !important;
}
.close-side-drawer-btn,
.open-side-drawer-btn {
  color: var(--q-primary);
  position: absolute;
  z-index: 1000;
}
.close-side-drawer-btn {
  top: 7px;
  right: 10px;
}
.open-side-drawer-btn {
  top: 9px;
  left: 10px;
}
.toggle-left-button {
  visibility: hidden !important;
}
.all-title {
  color: var(--greyscale-black-base, #000);
  font-family: SourceSansPro;
  font-size: 18px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
}

.new-chat-btn {
  font-family: SourceSansPro;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 142.857% */
}
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 200, 'GRAD' 0, 'opsz' 24;
}

.active {
  background-color: #66666615;
}

body,
div {
  font-family: 'SourceSansPro' !important;
}
:root {
  --bg-brand: #e6f7f6; //#b3e8e5;
  --bg-examples-brand: rgba(230, 247, 246, 0.31);
  --bg-examples-borders: #b3e8e5;
  --bg-examples-question-marks: rgb(1, 178, 170);
  --bg-examples-text: black;
  --brand: #2ab1ad;
  --text-brand: #444;
}

.bs-select__popup {
  width: auto !important;
  max-width: none !important;
  .q-item__label {
    padding-left: 1rem;
  }
}
.q-item {
  padding-left: 0 !important;
}

.q-item__section--side {
  padding-right: 0 !important;
}

.q-item__section--avatar {
  min-width: 20px !important;
}

.disabled.filters-selectors {
  cursor: pointer;
  .q-field__inner {
    background: #f5f5f5;
  }
}
.bs-alert-notification {
  border-radius: 4px;
  box-shadow: none;
}
.q-notification__icon--additional {
  margin-right: 8px;
}
.text-positive-alert {
  color: green !important;
}
.bg-positive-alert {
  background-color: #d7f0d6 !important;
}
.text-negative-alert {
  color: red !important;
}
.bg-negative-alert {
  background-color: #f9e3e5 !important;
}
.bs-font-medium-1-semi-bold {
  font-size: 12px;
  font-style: normal;
  font-weight: 600;
  line-height: 20px;
}
.content-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100%;
  width: 100%;
  justify-content: center;
  align-items: center;
  overflow-y: hidden;
}

.doc-intelligence-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-height: 100%;
}

.doc-intelligence-content,
.column.items-center {
  width: 80%;
  margin-top: 0px;
}

.doc-intelligence-content,
.column.items-center.loading {
  padding-top: 15px;
}

.dku-medium-title {
  width: 100%;
  max-width: 100%;
}

.filters-autoFilter .q-pa-sm {
  padding: 0px;
  margin-left: -15px;
}
.filters-autoFilter {
  margin-top: 21px;
}

.q-field__control-container {
  align-items: center !important;
}
.q-field__native {
  padding: 0px !important;
}

.filters-header {
  color: #333e48;
  font-size: 16px;
  font-weight: 600;
  margin-top: 20px;
}
.bs-toggle__content__active {
  background: #3b99fc !important;
}

.q-field--outlined {
  .q-field__control {
    &:before {
      border: none !important;
    }
    &:after {
      border: 1px solid #cccccc;
    }
    &:hover {
      &:before,
      &:after {
        border: 1px solid #999999;
      }
    }
  }
  &.q-field--highlighted {
    .q-field__control:after {
      border: 1px solid var(--brand);
    }
  }
}

.q-item {
  min-height: 20px;
  height: auto;
}
footer {
  width: 100%;
  padding: 20px;
  text-align: center;
}

.navigation-container {
  position: absolute;
  top: 20px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.navigation-container span {
  font-style: normal;
  font-weight: 600;
  font-size: 13px;
  line-height: 20px;
  color: #666666;
}

.navigation-container .q-icon {
  margin-left: 5px;
}

.clear-history-btn,
.settings-btn {
  top: 18px;
  right: 190px;
  cursor: pointer;
  z-index: 1;
  position: absolute;
  font-family: SourceSansPro;
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 142.857% */
}

.settings-btn {
  left: 50px;
  right: unset;
}

.clear-history-btn .q-icon,
.drawer-btn .q-icon,
.settings-btn {
  font-size: 18px;
}

.query-input {
  width: 100%;
}
.q-textarea.q-field--dense .q-field__control,
.q-textarea.q-field--dense .q-field__native {
  min-height: 28px !important;
  height: 28px;
  max-height: 300px;
}
@media screen and (orientation: landscape) and (max-height: 500px) and (max-width: 1000px),
  (max-width: 500px) {
  /* Styles for phone screens */
  .clear-history-btn {
    top: 8px;
    right: 16px;
  }
  .settings-btn{
    top: 8px;
  }
  .open-side-drawer-btn {
    top: 0px;
  }
  .btn-solution {
    bottom: 0px;
    top: unset !important;
    border: none !important;
  }
  .q-btn--outline::before {
    border: none !important;
  }
  footer {
    padding: 8px;
    margin-bottom: 24px;
  }
  .doc-content {
    max-width: 250px !important;
    min-width: auto !important;
    min-height: auto !important;
    height: auto !important;
    overflow: scroll;
    top: unset !important;
    bottom: 35px;
    padding: 20px 16px 10px 20px !important;
    .dku-large-title-sb {
      font-size: 20px !important;
    }
    .dku-small-title {
      font-size: 16px !important;
    }
    .dku-text {
      font-size: 12px;
    }
  }
  /* Adjusted width for smaller screens so that side bar takes all the screen */
  div.q-layout.q-layout--standard.bg-white {
    --bs-drawer-width: 100% !important;
  }
  .q-drawer.q-drawer--left.q-drawer--bordered.q-drawer--standard {
    width: 100% !important;
  }
}
.doc-footer__icon {
  padding-bottom: 6px !important;
  padding-top: 5px !important;
  border-bottom: 1px solid #f2f2f2;
}
.doc-footer__text {
  border-left: none !important;
  border-bottom: 1px solid #f2f2f2;
}

@media screen and (orientation: landscape) and (max-height: 500px) and (max-width: 1000px),
  (max-width: 767px) {
  /* Styles for phone screens */
  .doc-intelligence-content,
  .column.items-center {
    max-height: 100%;
    overflow-x: hidden;
  }
  .dku-medium-title {
    font-size: 16px;
  }
  .dku-grand-title-sb {
    font-size: 18px;
  }
  .doc-intelligence-content,
  .column.items-center {
    width: 100%;
    padding: 8px;
  }
  .navigation-container {
    top: 16px;
  }
  .btn-solution-text {
    font-size: 10px !important;
  }
}
</style>
