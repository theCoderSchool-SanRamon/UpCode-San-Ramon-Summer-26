<script setup>
import { onMounted, ref } from 'vue'
import Map from './map.vue'
import Search from './search.vue'
import Leaderboard from './Leaderboard.vue'
import PropertyPanel from './PropertyPanel.vue'
import CompareView from './CompareView.vue'

const mapRef = ref(null)

function handleSelect(selection) {
	if (!mapRef.value) return
	if (selection.type === 'county') {
		mapRef.value.goToCounty(selection.key)
	} else if (selection.type === 'point') {
		mapRef.value.goToCoordinate(selection.lon, selection.lat)
	}
}
</script>

<template>

<div id="layer_root_overlay">

	<div id="toolbar_container">



	</div>

	<Search id="search" :counties="mapRef?.countyList ?? []" @select="handleSelect" />
	<PropertyPanel />
	<!-- <Leaderboard :counties="mapRef?.countyList ?? []" @select="handleSelect" /> -->
	<CompareView />
</div>
<Map id='map' ref="mapRef" />

</template>

<style scoped>
#map {
		height: 100%;
		width: 100%;
		position: fixed;
}
#search_button {
	background: var(--overlay-background)
}
</style>