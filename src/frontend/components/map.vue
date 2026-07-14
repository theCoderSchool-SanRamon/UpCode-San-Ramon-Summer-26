<script setup>
import { onMounted, ref } from 'vue'
import Map from 'ol/Map.js'
import OSM from 'ol/source/OSM.js'
import TileLayer from 'ol/layer/Tile.js'
import View from 'ol/View.js'
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import { defaults as defaultControls } from 'ol/control.js';
import { Style, Fill, Stroke } from 'ol/style';

const mapRoot = ref(null)

let mapInstance = null
let OSMLayer = null

const countySource = new VectorSource()
const countylayer = new VectorLayer({
	source: countySource
})

function getColor(d, m, i) {
	return isNaN(d) ? '#CFCFCF' : getColorMix(
		(100 * (Math.min(d, m) / m)) < 50 ? `color-mix(
		in srgb, 
		${i ? 'red' : 'green'}, 
		yellow ${(100 * (Math.min(d, m) / m)) * 2}%)`
		: `color-mix(
		in srgb, 
		yellow, 
		${i ? 'green' : 'red'} ${((100 * (Math.min(d, m) / m)) - 50) * 2}%)`
	);
}

function getColorMix(s) {
	const cnv = document.createElement("canvas").getContext("2d");
	cnv.fillStyle = s;
	return cnv.fillStyle;
}

onMounted(async () => {

	OSMLayer = new TileLayer({
		source: new OSM(),
	}),
	
	mapInstance = new Map({
		target: mapRoot.value,
		controls: defaultControls({ zoom: false }),
		layers: [
			OSMLayer,
	 ],
		view: new View({
			center: [0, 0],
			zoom: 2, }),
	});

	var countyGeometry = await fetch("/counties.geojson", {headers: {'Content-Type': 'application/json'}});
	countyGeometry = await countyGeometry.json() 
	const features = new GeoJSON().readFeatures(
			countyGeometry, 
			{featureProjection: 'EPSG:3857', }
		)
	
	countySource.addFeatures(features)
	//countylayer.setStyle()
	mapInstance.addLayer(countylayer)
})

defineExpose({
	mapInstance,
	OSMLayer,
})

</script>

<template>
	<div class="map" ref="mapRoot"></div>
</template>

<style scoped>
</style>