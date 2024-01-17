<template>
  <footer class="dku-tiny-text">
    {{ disclaimerText }}
    <span style="color: #267cfb; text-decoration: underline">Responsible AI</span>
    considerations
  </footer>
</template>
<script lang="ts">
export default {
  data() {
    return {
      disclaimerText: ''
    }
  },
  methods: {
    adjustDisclaimer() {
      if (window.innerWidth <= 600 || screen.orientation.type.indexOf("landscape") >= 0) {
        this.disclaimerText = 'Outputs from a Large Language Model, review proposed outcomes in context with'
      } else {
        this.disclaimerText = `This business application generates outputs from a Large Language Model. As
        a user of this application, you are encouraged to review proposed outcomes
        and adjust them in light of your specific business context and`
      }
    }
  },
  mounted() {
    this.adjustDisclaimer()
    window.addEventListener('resize', this.adjustDisclaimer)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.adjustDisclaimer)
  }
}
</script>
<style></style>
