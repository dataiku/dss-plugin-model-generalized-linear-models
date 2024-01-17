<template>
  <q-expansion-item
    :label="$t('sources')"
    v-model="expanded"
    header-class="expansion-item"
    switch-toggle-side
    class="sources-expansion-item"
  >
    <div class="source-item">
      <div v-for="(source, index) in sources" :key="index" class="source-text">
        <div class="source-meta">
          <img
            class="source-thumbnail"
            :src="(source.metadata.source_thumbnail_url as string)"
            v-if="source.metadata?.source_thumbnail_url"
          />
          <div>
            <span>{{ `${index + 1}. ` }} </span>
            <span v-if="getUrlFromSource(source)">
              <a :href="getUrlFromSource(source)" target="_blank" class="source-link">
                <span v-html="getSourceTitle(source)" class="source-title"></span>
              </a>
            </span>
            <span v-html="getSourceTitle(source)" v-else class="source-title"></span>
          </div>
        </div>
        <div v-html="convertNewlinesToHTML(source.excerpt)" style="padding-left: 6px"></div>
        <Tags :tags="getSourceTags(source)" v-if="source.metadata?.tags" />
      </div>
    </div>
  </q-expansion-item>
</template>
<script lang="ts">
import { defineComponent } from 'vue'
import type { Source } from '@/models'
import Tags from './Tags.vue'

type MimeMap = Map<string, string>
const urlRegex =
  /(?:https?|ftp):\/\/[\S]+|(www\.[\S]+)|(?:\b\w+\.\w{2,}(?::\d{1,5})?(?:\/[\S]*)?\b)/gi
const commonMimeTypes: MimeMap = new Map([
  ['pdf', 'application/pdf'],
  ['ppt', 'application/vnd.ms-powerpoint'],
  ['csv', 'text/csv'],
  ['xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
  ['txt', 'text/plain']
])

export default defineComponent({
  props: {
    sources: {
      type: Array as () => Source[],
      required: true
    },
    projectKey: {
      type: String,
      default: ''
    },
    folderId: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      expanded: false
    }
  },
  methods: {
    getSourceTitle(source: Source) {
      if (!source.metadata) {
        return ''
      }

      const { source_title, page, score } = source.metadata
      if (!source_title) {
        return ''
      }

      const metadataParts = []
      if (page) {
        metadataParts.push(`Page: ${page}`)
      }
      if (score) {
        metadataParts.push(`Similarity Score: ${score}`)
      }

      const metadataString = metadataParts.length > 0 ? `, ${metadataParts.join(', ')}` : ''
      return `${source_title}${metadataString}`
    },
    getUrlFromSource(source: Source): string {
      const src = (
        source.metadata.source_url ? source.metadata.source_url : source.metadata.source_title
      ) as string
      // Check if the source is just a filename (e.g., ends in .pdf, .docx, etc.)
      if (this.isFileName(src)) {
        // Extract file extension
        const fileExtension = src.split('.').pop()?.toLowerCase() || ''
        let endpoint = ''
        const contentType = commonMimeTypes.get(fileExtension) || 'application/octet-stream'
        if (fileExtension === 'pdf') {
          // Fetch the content type based on the file extension
          endpoint = `dip/api/managedfolder/preview-image?contextProjectKey=${
            this.projectKey
          }&itemPath=${encodeURIComponent(src)}&projectKey=${this.projectKey}&odbId=${
            this.folderId
          }&contentType=${contentType}`
        } else {
          endpoint = `projects/${this.projectKey}/managedfolder/${this.folderId}/view/`
        }
        return `/${endpoint}`
      }
      const detectedUrl = this.getUrlFromString(src)
      return detectedUrl
    },
    isFileName(str: string): boolean {
      return /\.(pdf|docx|doc|xls|xlsx|ppt|pptx|txt|csv)$/i.test(str)
    },
    getUrlFromString(txt: string): string {
      const urls = txt.match(urlRegex) || []
      return urls.length > 0 ? (urls[0] as string) : ''
    },
    getDomainFromUrl(url: string): string {
      const match = url.match(/^(?:https?:\/\/)?(www\.)?([^\/]+)/i)
      return match ? match[0] : ''
    },
    convertNewlinesToHTML(str: string): string {
      const lines = str.split('\n\n')
      let convertedString = lines[0]
      for (let i = 1; i < lines.length; i++) {
        convertedString += "<div style='margin-bottom: 6px;'>" + lines[i] + '</div>'
      }
      return convertedString
    },
    getSourceTags(source: Source) {
      if (source.metadata && source.metadata.tags) {
        const tags = {} as any
        ;(source.metadata.tags as any[]).forEach(
          (el: { name: string; value: string; type: string }) =>
            (tags[el.name] = el.type === 'string' ? [el.value] : [...el.value])
        )
        return tags
      }
    }
  },
  watch: {
    expanded(newVal) {
      this.$emit('update:expanded', newVal)
    }
  },
  components: { Tags }
})
</script>
<style scoped>
.expansion-item {
  font-style: normal;
  font-weight: 600;
  font-size: 20px;
  line-height: 15px;
  color: #666666;
  width: 100%;
}
.sources-expansion-item {
  margin-top: 10px;
  font-size: 12px;
  /* color: teal; */
  margin-left: -4px;
  color: #444;
  font-weight: bold;
}
:deep(.q-item) {
  padding: 4px;
}
:deep(.q-item__section--side > .q-icon) {
  font-size: 16px;
}
.source-item {
  margin-top: 5px;
  margin-bottom: 5px;
}
.source-text {
  font-style: normal;
  font-weight: 400;
  font-size: 11px;
  line-height: 16px;
  /* color: teal; */
  color: #444;
  margin-bottom: 16px;
}
.source-meta {
  margin-left: 4px;
  margin-bottom: 10px;
  font-weight: 600;
  display: inline-flex;
  gap: 10px;
}
.source-link {
  color: #666666;
  font-weight: 500;
  /* color: teal; */
  color: #444;
}
.source-thumbnail {
  width: 100px;
  height: 60px;
  overflow: hidden;
}
</style>
