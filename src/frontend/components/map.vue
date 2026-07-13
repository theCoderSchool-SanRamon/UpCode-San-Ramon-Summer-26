<script setup>
import { onMounted, ref } from 'vue'
import Map from 'ol/Map.js'
import OSM from 'ol/source/OSM.js'
import TileLayer from 'ol/layer/Tile.js'
import View from 'ol/View.js'

const mapRoot = ref(null)

let mapInstance = null

onMounted(() => 
	{
		mapInstance = new Map({
		target: mapRoot.value,
		layers: [
			new TileLayer({
				source: new OSM(),
			}),
		],
		view: new View({
			center: [0, 0],
			zoom: 2,
		}),
	});
}
)
</script>

<template>
	<div class="map" ref="mapRoot"></div>
</template>

<style scoped>
	.map {
		width: 400px;
		height: 400px;
	}
</style>