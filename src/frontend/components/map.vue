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
let pricerent = ref(null)

let mapInstance = null
let OSMLayer = null


const countySource = new VectorSource()
const countylayer = new VectorLayer({
	source: countySource,
	style: styleFeature,
	opacity: 0.7,
})

function styleFeature(feature) {
		const id = feature.get("STATEFP") + feature.get("COUNTYFP")
		const col = getColor((Number(pricerent[id][0]) / Number(pricerent[id][1]))/12,60,false)
		return new Style({
			fill: new Fill({
				color: col,
			}),
			stroke: new Stroke({
				color: '#00000053',
				width: 0.1,
			})
		})
	}

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
			center: [-11281117, 4579425],
			zoom: 5, }),
	});

	var countyGeometry = fetch("/counties.geojson", {headers: {'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=2628000, immutable'}});
	var priceandrentf = fetch("/api/census?query=B25077_001E,B25058_001E&county=*")

	countyGeometry = await countyGeometry
	priceandrentf = await priceandrentf

	countyGeometry = await countyGeometry.json()
	pricerent = await priceandrentf.json()
	
	const features = new GeoJSON().readFeatures(
			countyGeometry, 
			{featureProjection: 'EPSG:3857', }
		)
	
	countySource.addFeatures(features)

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