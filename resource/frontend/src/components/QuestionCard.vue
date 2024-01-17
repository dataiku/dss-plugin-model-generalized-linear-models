<template>
  <div class="query-container q-pa-sm self-start" v-if="query">
    <div class="column query-section">
      <div class="row no-wrap">
        <q-avatar color="brand" text-color="white" icon="person" size="sm" />
        <div>
          <span class="query-text" v-html="queryEl"></span>
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import CodeDisplay from './CodeDisplay.vue'

export default defineComponent({
  props: {
    query: {
      type: String,
      required: true
    }
  },
  methods: {
    escapeHTML(str: string) {
      return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
    }
  },
  computed: {
    queryEl() {
      // Detect URLs and make them clickable
      const urlRegex = /(https?:\/\/|www\.)[^\s]+/g
      return this.escapeHTML(this.query)
        .replace(
          urlRegex,
          (url) => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
        )
        .replace(/\n/g, '<br>')
    }
  },
  components: { CodeDisplay }
})
</script>
<style>
.bg-brand {
  background: var(--brand);
}
.query-container {
  /* brand color */
  /* background: var(--bg-brand);  */
  background: var(--bg-brand);
  /* background: rgba(4,30,58, 0.5); */
  border-radius: 6px;
  max-width: 95%;
  width: auto;
  align-self: flex-end;
  color: var(--text-brand);
  word-wrap: break-word;
}

.query-section {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
/* For portrait */
@media (max-width: 767px) {
  .query-container {
    max-width: 90%;
  }
}
.query-text {
  font-style: normal;
  font-weight: 400;
  font-size: 13px;
  line-height: 20px;
  overflow-x: hidden;
  margin-left: 0.5rem;
  white-space: pre-wrap;
}
</style>
