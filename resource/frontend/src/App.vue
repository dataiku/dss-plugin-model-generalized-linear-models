<script lang="ts">
import { ServerApi } from '@/api/server_api'
import { RouterView } from 'vue-router'
export default {
  async created() {
    const LOCAL_BACKEND_URL = 'http://127.0.0.1:5000'
    let dataikuLib
    try {
      // @ts-ignore
      // eslint-disable-next-line no-undef
      dataikuLib = dataiku
    } catch (e) {
      dataikuLib = undefined
    }
    let host = ''
    const isLocal = !dataikuLib
    if (!isLocal) {
      await (async () => {
        while (!dataikuLib?.getWebAppBackendUrl) {
          await new Promise((resolve) => setTimeout(resolve, 1000))
        }
        host = dataikuLib.getWebAppBackendUrl('/')
      })()
    } else {
      host = LOCAL_BACKEND_URL
    }
    ServerApi.init({ host })
  },
  components: {
    RouterView
  }
}
</script>
<template>
  <RouterView />
</template>
