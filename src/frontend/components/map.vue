<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import Map from 'ol/Map.js'
import OSM from 'ol/source/OSM.js'
import TileLayer from 'ol/layer/Tile.js'
import View from 'ol/View.js'
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import { defaults as defaultControls } from 'ol/control.js';
import { Style, Fill, Stroke } from 'ol/style';
import { fromLonLat } from 'ol/proj.js';
import { useCountyScores } from '../composables/countyScores.js'

const { countyScores, keyFor, ensureLoaded: ensureScoresLoaded, populationFilter, POPULATION_THRESHOLDS } = useCountyScores()

const mapRoot = ref(null)
let countyData = ref(null)

let mapInstance = null
let OSMLayer = null

const countyList = ref([])
let countyFeaturesById = {}
const highlightedId = ref(null)

const isHovering = ref(false)
const mouseX = ref(0)
const mouseY = ref(0)
const hoveredFeature = ref(null)

const hoverInfo = computed(() => {
	const f = hoveredFeature.value
	if (!f) return null
	const id = getCountyId(f)
	const data = countyData && countyData[id]
	const houseprice = data && data[0] > 0 ? Number(data[0]) : null
	const rent = data && data[1] > 0 ? Number(data[1]) : null
	const population = data && data[2] != null ? Number(data[2]) : null
	const scoreInfo = countyScores.value[keyFor(f.get("NAME"), f.get("STUSPS"))]
	return {
		name: f.get("NAME"),
		state: f.get("STUSPS"),
		houseprice,
		rent,
		population,
		ratio: (houseprice != null && rent) ? houseprice / rent / 12 : null,
		score: scoreInfo?.score ?? null,
		filtered: !countyMeetsThreshold(id, POPULATION_THRESHOLDS[populationFilter.value]),
	}
})


const countySource = new VectorSource()
const countylayer = new VectorLayer({
	source: countySource,
	style: styleFeature,
	opacity: 0.7,
})

function getCountyId(feature) {
	return feature.get("STATEFP") + feature.get("COUNTYFP")
}

function countyMeetsThreshold(id, threshold) {
	if (threshold <= 0) return true
	const pop = countyData?.[id]?.[2]
	return pop != null && Number(pop) >= threshold
}

function styleFeature(feature) {
		const id = getCountyId(feature)
		const fillColor = countyMeetsThreshold(id, POPULATION_THRESHOLDS[populationFilter.value])
			? getColor((Number(countyData[id][0]) / Number(countyData[id][1]))/12,60,false)
			: '#B5B5B5'
		const isHighlighted = id === highlightedId.value
		return new Style({
			fill: new Fill({ color: fillColor }),
			stroke: new Stroke(
				isHighlighted
					? { color: '#F0CC00', width: 8 }
					: { color: '#00000053', width: 0.4 }
			),
			zIndex: isHighlighted ? 1 : 0
		})
	}

function getColor(d, m, i) {
	return d <= 1 ? '#CFCFCF' : getColorMix(
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
	ensureScoresLoaded()

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
	var priceandrentf = fetch("/api/census?query=B25077_001E,B25058_001E,B01003_001E&county=*")

	countyGeometry = await countyGeometry
	priceandrentf = await priceandrentf

	countyGeometry = await countyGeometry.json()
	countyData = await priceandrentf.json()

	const features = new GeoJSON().readFeatures(
			countyGeometry,
			{featureProjection: 'EPSG:3857', }
		)

	countySource.addFeatures(features)

	countyFeaturesById = {}
	const counties = []
	for (const feature of features) {
		const key = getCountyId(feature)
		countyFeaturesById[key] = feature
		counties.push({ name: feature.get("NAME"), state: feature.get("STUSPS"), key })
	}
	counties.sort((a, b) => a.name.localeCompare(b.name) || a.state.localeCompare(b.state))
	countyList.value = counties

	mapInstance.addLayer(countylayer)

	mapInstance.on('pointermove', (evt) => {
		mouseX.value = evt.originalEvent.clientX
		mouseY.value = evt.originalEvent.clientY
		const feature = mapInstance.forEachFeatureAtPixel(evt.pixel, f => f, { layerFilter: l => l === countylayer })
		hoveredFeature.value = feature ?? null
		isHovering.value = !!feature
		if (highlightedId.value != null && isHovering.value) {highlightedId.value = null}
	})
	mapInstance.getViewport().addEventListener('mouseout', () => { isHovering.value = false })
})

watch(populationFilter, () => countylayer.changed())
watch(highlightedId, () => countylayer.changed())

function goToCounty(key) {
	const feature = countyFeaturesById[key]
	if (!feature) return
	highlightedId.value = key
	mapInstance.getView().fit(feature.getGeometry().getExtent(), { padding: [40, 40, 40, 40], maxZoom: 10, duration: 400 })
}

function goToCoordinate(lon, lat, zoom = 11) {
	highlightedId.value = null
	mapInstance.getView().animate({ center: fromLonLat([lon, lat]), zoom, duration: 400 })
}

defineExpose({
	mapInstance,
	OSMLayer,
	countyList,
	goToCounty,
	goToCoordinate,
})

</script>

<template>
	<div class="map" ref="mapRoot">
		<div class="hover-box" v-if="isHovering && hoverInfo" :style="{ left: mouseX + 12 + 'px', top: mouseY + 20 + 'px' }">
			<h3>{{ hoverInfo.name }}, {{ hoverInfo.state }}</h3>
			<template v-if="hoverInfo.filtered"><i>Filtered: population below threshold</i><br></template>
			Price/Rent Ratio: <b>{{ hoverInfo.ratio == null ? "N/A" : hoverInfo.ratio.toFixed(2) }}</b><br>
			Median Contract Rent: $<b>{{ hoverInfo.rent == null ? "N/A" : hoverInfo.rent }}</b>/mo<br>
			Median House Price: $<b>{{ hoverInfo.houseprice == null ? "N/A" : hoverInfo.houseprice }}</b><br>
			Population: <b>{{ hoverInfo.population != null ? hoverInfo.population.toLocaleString() : 'N/A' }}</b><br>
			<template v-if="hoverInfo.score != null">Investment Score: <b>{{ hoverInfo.score.toFixed(1) }}</b></template>
			<!--<template v-else>No price/rent data</template>-->
		</div>
		<div class="population-filter">
			<label for="population-filter-select">Min. county population:</label>
			<select id="population-filter-select" v-model="populationFilter">
				<option value="all">All</option>
				<option value="50k">50k+</option>
				<option value="100k">100k+</option>
				<option value="250k">250k+</option>
				<option value="500k">500k+</option>
			</select>
		</div>
	</div>
</template>

<style scoped>
.hover-box {
	z-index: 90;
	pointer-events: none;
	position: fixed;
	padding: 6px 8px;
	font: 14px/16px Arial, Helvetica, sans-serif;
	background: var(--overlay-background);
	backdrop-filter: blur(5px);
	box-shadow: 0 0 15px rgba(0,0,0,0.2);
	border-radius: 5px;
	user-select: none;
}
.hover-box h3 {
	margin: 0 0 5px;
}
.population-filter {
	position: absolute;
	bottom: 60px;
	left: 24px;
	z-index: 100;
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 14px;
	background: var(--overlay-background);
	backdrop-filter: blur(5px);
	border: 1px solid #ccc;
	border-radius: 12px;
	font: 14px Arial, sans-serif;
	color: #555;
	pointer-events: auto;
}
.population-filter select {
	font: 14px Arial, sans-serif;
	border: 1px solid #ccc;
	border-radius: 6px;
	padding: 5px 8px;
	outline: none;
	background: white;
	cursor: pointer;
}
.population-filter select:focus {
	border-color: #666;
}
</style>
