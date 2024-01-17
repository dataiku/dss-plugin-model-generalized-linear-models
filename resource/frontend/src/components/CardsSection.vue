<template>
  <div class="row no-wrap q-gutter-x-md">
    <InfoCard :text="infoText1" />
    <InfoCard :text="infoText2" />
    <InfoCard :text="infoText3" />
  </div>
</template>
<script setup lang="ts">
import InfoCard from './InfoCard.vue'

const infoText1 =
  '“Which company was most exposed to environmental risk between New Senior Investment and National Presto in 2019”'
const infoText2 = '“What environmental risks is NextCure facing in 2021”'
const infoText3 =
  '“What is Brown & Brown policy to encourage gender equality and mitigate discrimination”'
</script>
<style lang="sass" scoped></style>
