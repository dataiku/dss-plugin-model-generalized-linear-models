<template>
  <div class="bs-truncate-text" @mouseover="showTooltip">
    <slot></slot>
    <BsTooltip v-if="isOverflowing" class="bs-tooltip"> {{ tooltipContent }}</BsTooltip>
  </div>
</template>

<script lang="ts">
import { BsTooltip } from 'quasar-ui-bs'

export default {
  name: 'BSTruncatedText',
  components: {
    BsTooltip
  },
  props: {
    tooltipContent: String
  },
  data() {
    return {
      isOverflowing: false
    }
  },
  mounted() {
    this.isOverflowing = this.checkOverflow()
  },
  methods: {
    showTooltip() {
      if (this.checkOverflow()) {
        this.isOverflowing = true
      } else {
        this.isOverflowing = false
      }
    },
    checkOverflow(): boolean {
      return (
        this.$el.offsetWidth < this.$el.scrollWidth || this.$el.offsetHeight < this.$el.scrollHeight
      )
    }
  }
}
</script>

<style scoped>
.bs-truncate-text {
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  position: relative;
}
</style>
