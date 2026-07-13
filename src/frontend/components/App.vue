<script setup>
import { onMounted, ref } from 'vue'
import Map from './map.vue'

</script>

<template>

<div id="layer_root_overlay"></div>
<Map id="map" />

</template>

<style scoped>
#map {
		height: 100%;
		width: 100%;
		position: fixed;
}

</style>