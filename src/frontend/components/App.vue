<script setup>
import { ref } from 'vue'
import Map from './map.vue'
import Search from './Search.vue'
import Leaderboard from './Leaderboard.vue'
import PropertyPanel from './PropertyPanel.vue'
import CompareView from './CompareView.vue'
import LayerControl from './LayerControl.vue'
import Filter from './Filter.vue'
import ToolToggle from './ToolToggle.vue'
import DetailBox from './DetailBox.vue'
import About from './About.vue'
import { Analytics } from '@vercel/analytics/vue'
import ChatWidget from './ChatWidget.vue'

const mapRef = ref(null)
const detailBoxRef = ref(null)
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
	else if (change.type === "interactability") {
		mapRef.value.setInteractable(change.layer, change.value)
	} else if (change.type === "heatmap") {
		mapRef.value.heatmapShows = change.value
	}
}

function handleTriggerDetail(feature, place) {
	detailBoxRef.value.activateDetail(feature, place)
}
</script>

<template>

<Analytics />

<div id="layer_root_overlay">
	<div id="toolbar_container">

		<Search id="search" :counties="mapRef?.countyList ?? []" @select="handleSelect" />
		<LayerControl @changed="handleLayerControlChanged"/>
		<Filter />
		<ToolToggle :icon="'/ranking.svg'" @changed="(change) => showLeaderboard=change.value" />
		<About />
	</div>
	<DetailBox ref="detailBoxRef" />
	<Leaderboard :counties="mapRef?.countyList ?? []" @select="handleSelect" v-show="showLeaderboard" />
	<ChatWidget />
	<PropertyPanel />

	<CompareView />
</div>

<Map id='map' ref="mapRef" @trigger-detail="handleTriggerDetail" />

</template>

<style scoped>

#toolbar_container {
	position: fixed;
	flex-direction: row;
	flex: content;
	width: 100%;
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