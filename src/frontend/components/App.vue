<script setup>
import { onMounted, ref } from 'vue'
import Map from './map.vue'
import Search from './search.vue'
import Leaderboard from './Leaderboard.vue'
import PropertyPanel from './PropertyPanel.vue'
import CompareView from './CompareView.vue'
import LayerControl from './LayerControl.vue'
import Filter from './Filter.vue'
import ToolToggle from './ToolToggle.vue'

const mapRef = ref(null)
const showLeaderboard = ref(false)

function handleSelect(selection) {
	if (!mapRef.value) return
	if (selection.type === 'county') {
		mapRef.value.goToCounty(selection.key)
	} else if (selection.type === 'point') {
		mapRef.value.goToCoordinate(selection.lon, selection.lat)
	}
}

function handleLayerControlChanged(change) {
	if (!mapRef.value) return
	if (change.type === "visibility") {
		mapRef.value.setVisible(change.layer, change.value)
	}
	if (change.type === "interactability") {
		mapRef.value.setInteractable(change.layer, change.value)
	}
}

function handleFilterChanged(change) {
	if (!mapRef.value) return
	if (change.type === "populationfilter") {
		mapRef.value.populationFilter.value = change.value
	}
}

</script>

<template>

<div id="layer_root_overlay">

	<div id="toolbar_container">

		<Search id="search" :counties="mapRef?.countyList ?? []" @select="handleSelect" />
		<LayerControl id="layer-control" @changed="handleLayerControlChanged"/>
		<Filter />
		<ToolToggle @changed="(change) => showLeaderboard=change.value" />

	</div>
	<Leaderboard :counties="mapRef?.countyList ?? []" @select="handleSelect" v-show="showLeaderboard" />
	<!--<PropertyPanel />-->
	
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