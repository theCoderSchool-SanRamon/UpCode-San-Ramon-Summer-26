<script setup>
import { onMounted, ref } from 'vue'
import Map from './map.vue'
import Search from './search.vue'
import Leaderboard from './Leaderboard.vue'
import PropertyPanel from './PropertyPanel.vue'
import CompareView from './CompareView.vue'
import LayerControl from './LayerControl.vue'
import Filter from './Filter.vue'

const mapRef = ref(null)

function handleSelect(selection) {
	if (!mapRef.value) return
	if (selection.type === 'county') {
		mapRef.value.goToCounty(selection.key)
	} else if (selection.type === 'point') {
		mapRef.value.goToCoordinate(selection.lon, selection.lat)
	}
}

function handleLayerControlChanged(change) {
	console.log(change)
	if (!mapRef.value) return
	if (change.type === "visibility") {
		mapRef.value.setVisible(change.layer, change.value)
	}
	if (change.type === "interactability" && change.value) {
		mapRef.value.setInteractable(change.layer)
	}
}
</script>

<template>

<div id="layer_root_overlay">

	<div id="toolbar_container">

		<Search id="search" :counties="mapRef?.countyList ?? []" @select="handleSelect" />
		<LayerControl id="layer-control" @changed="handleLayerControlChanged"/>

		<Filter />

	</div>

	<!--<PropertyPanel />-->
	<!-- <Leaderboard :counties="mapRef?.countyList ?? []" @select="handleSelect" /> -->
	<CompareView />
</div>

<Map id='map' ref="mapRef" />

</template>

<style scoped>

#toolbar_container {
	position: fixed;
	flex-direction: row;
	flex: content;
	display: flex;
	flex-wrap: nowrap;
}

#map {
		height: 100%;
		width: 100%;
		position: fixed;
}
#search_button {
	background: var(--overlay-background)
}
</style>