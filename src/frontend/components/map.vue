<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import Map from 'ol/Map.js'
import OSM from 'ol/source/OSM.js'
import TileLayer from 'ol/layer/Tile.js'
import View from 'ol/View.js'
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import Feature from 'ol/Feature.js';
import Point from 'ol/geom/Point.js';
import { defaults as defaultControls } from 'ol/control.js';
import { Style, Fill, Stroke, Text } from 'ol/style';
import { fromLonLat, toLonLat } from 'ol/proj.js';
import { useCountyScores } from '../composables/countyScores.js'
import { usePropertyAnalysis } from '../composables/propertyAnalysis.js'

const { countyScores, keyFor, ensureLoaded: ensureScoresLoaded, populationFilter} = useCountyScores()
const { fetchProperty, addressQuery } = usePropertyAnalysis()

const emit = defineEmits(["triggerDetail"])

const heatmapShows = ref("pricerent")
const mapRoot = ref(null)
let countyData = ref(null)
let placeData = ref(null)
const maxPopulation = ref(1)

let mapInstance = null
let OSMLayer = null

const countyList = ref([])
let countyFeaturesById = {}
const highlightedId = ref(null)
let countyActive = true
let cityActive = true

const isHovering = ref(false)
const mouseX = ref(0)
const mouseY = ref(0)
const hoveredFeature = ref(null)
const isHoveringPlace = ref(false)
const loading = ref(true)

const hoverInfo = computed(() => {
	const f = hoveredFeature.value
	if (!f) return null
	const id = isHoveringPlace.value ? getPlaceId(f) : getCountyId(f)
	const data = isHoveringPlace.value ? placeData && placeData[id] : countyData && countyData[id]
	const houseprice = data && data[0] > 0 ? Number(data[0]) : null
	const rent = data && data[1] > 0 ? Number(data[1]) : null
	const population = data && data[2] != null ? Number(data[2]) : null
	const scoreInfo = isHoveringPlace.value ? null : countyScores.value[keyFor(f.get("NAME"), f.get("STUSPS"))]
	return {
		name: f.get("NAME"),
		state: f.get("STUSPS"),
		houseprice,
		rent,
		population,
		ratio: (houseprice != null && rent) ? houseprice / rent / 12 : null,
		score: scoreInfo?.score ?? null,
		filtered: !countyMeetsThreshold(id, populationFilter.value),
	}
})


const countySource = new VectorSource()
const countylayer = new VectorLayer({
	source: countySource,
	style: styleCountyFeature,
	opacity: 0.7,
})
const placeSource = new VectorSource()
const placelayer = new VectorLayer({
	source: placeSource,
	style: stylePlaceFeature,
	opacity: 0.7,
	minZoom: 7,
})

const LISTINGS_MIN_ZOOM = 12
const LISTINGS_BUCKET_STEP = 0.05

const listingsSource = new VectorSource()
const listingsLayer = new VectorLayer({
	source: listingsSource,
	style: styleListing,
})
listingsLayer.setVisible(false)

const fetchedListingBuckets = new Set()
const seenListingAddresses = new Set()

function formatPriceShort(v) {
	if (v == null) return '?'
	if (v >= 1e6) return '$' + (v / 1e6).toFixed(2) + 'M'
	if (v >= 1e3) return '$' + Math.round(v / 1e3) + 'K'
	return '$' + v
}

function styleListing(feature) {
	return new Style({
		text: new Text({
			text: formatPriceShort(feature.get('price')),
			font: 'bold 12px Arial, sans-serif',
			fill: new Fill({ color: '#ffffff' }),
			backgroundFill: new Fill({ color: '#7a1f1f' }),
			backgroundStroke: new Stroke({ color: '#4a1010', width: 1 }),
			padding: [4, 8, 4, 8],
		}),
	})
}

function listingBucketKey(lat, lon, radius) {
	const blat = Math.round(lat / LISTINGS_BUCKET_STEP) * LISTINGS_BUCKET_STEP
	const blon = Math.round(lon / LISTINGS_BUCKET_STEP) * LISTINGS_BUCKET_STEP
	return `${blat.toFixed(2)},${blon.toFixed(2)},${Math.round(radius)}`
}

async function fetchListings(lat, lon, radiusMiles) {
	const key = listingBucketKey(lat, lon, radiusMiles)
	if (fetchedListingBuckets.has(key)) return
	fetchedListingBuckets.add(key)
	try {
		const res = await fetch(`/api/listings?lat=${lat}&lon=${lon}&radius=${radiusMiles}`)
		if (!res.ok) return
		const listings = await res.json()
		const features = []
		for (const l of listings) {
			if (l.latitude == null || l.longitude == null || !l.price || !l.address) continue
			if (seenListingAddresses.has(l.address)) continue
			seenListingAddresses.add(l.address)
			const feature = new Feature({ geometry: new Point(fromLonLat([l.longitude, l.latitude])) })
			feature.set('address', l.address)
			feature.set('price', l.price)
			feature.set('beds', l.beds)
			feature.set('baths', l.baths)
			feature.set('sqft', l.sqft)
			features.push(feature)
		}
		listingsSource.addFeatures(features)
	} catch (e) {} // silently skip; listings are a best-effort overlay
}

function getCountyId(feature) {
	return feature.get("STATEFP") + feature.get("COUNTYFP")
}

function getPlaceId(feature) {
	return feature.get("STATEFP") + feature.get("PLACEFP")
}

function countyMeetsThreshold(id, threshold) {
	if (threshold <= 0) return true
	const pop = countyData?.[id]?.[2]
	return pop != null && Number(pop) >= threshold
}

function styleCountyFeature(feature) {
	const id = getCountyId(feature)
	let dataPoint
	let colorMax = 60
	let inverted = false
	switch (heatmapShows.value) {
		case "pricerent":
			dataPoint = (Number(countyData[id][0]) / Number(countyData[id][1]))/12
			colorMax = 60
			inverted = false // low ratio (cheap relative to rent) is good -> green
			break;
		case "score":
			dataPoint = countyScores.value[keyFor(feature.get("NAME"), feature.get("STUSPS"))]?.score ?? 0
			colorMax = 100
			inverted = true // high score is good -> green
			break;
		case "population":
			console.log(Math.log(Number(countyData[id][2]) / 100) / Math.log(4000000 / 100))
			dataPoint = Math.log(Number(countyData[id][2]) / 100) / Math.log(4000000 / 100)
			colorMax = 1
			inverted = true // more population is good -> green
			break;
	}

	const fillColor = countyMeetsThreshold(id, populationFilter.value)
		? getColor(dataPoint, colorMax, inverted)
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

function stylePlaceFeature(feature) {
	try {
		const id = getPlaceId(feature)
		const fillColor = true // countyMeetsThreshold(id, POPULATION_THRESHOLDS[populationFilter.value])
			? getColor((Number(placeData[id][0]) / Number(placeData[id][1])) / 12, 60, false)
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
	} catch(e) {
		return new Style({
			fill: new Fill({ color: '#B5B5B5' }),
			stroke: new Stroke(
				{ color: '#00000053', width: 0.4 }
			),
			zIndex: 0
		})
	}
}

function getColor(d, m, i) {
	return d <= 0 ? '#CFCFCF' : getColorMix(
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
			zoom: 5, 
			maxZoom: 20, }),
	});

	var countyGeometry = fetch("/counties.geojson", {headers: {'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=2628000, immutable'}});
	var placeGeometry = fetch("/places.geojson", {headers: {'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=2628000, immutable'}})
	var priceandrentcounty = fetch("/api/census?query=B25077_001E,B25058_001E,B01003_001E&county=*")
	var priceandrentplace = fetch("/api/census?query=B25077_001E,B25058_001E,B01003_001E&place=*")

	countyGeometry = await countyGeometry
	placeGeometry = await placeGeometry
	priceandrentcounty = await priceandrentcounty
	priceandrentplace = await priceandrentplace

	countyGeometry = await countyGeometry.json()
	placeGeometry = await placeGeometry.json()
	countyData = await priceandrentcounty.json()
	placeData = await priceandrentplace.json()
	maxPopulation.value = Math.max(1, ...Object.values(countyData).map(c => Number(c[2]) || 0))

	var countyFeatures = new GeoJSON().readFeatures(
			countyGeometry,
			{featureProjection: 'EPSG:3857', }
		)

	countySource.addFeatures(countyFeatures)

	var placeFeatures = new GeoJSON().readFeatures(
			placeGeometry,
			{featureProjection: 'EPSG:3857', }
		)
	placeSource.addFeatures(placeFeatures)

	countyFeaturesById = {}
	const counties = []
	for (const feature of countyFeatures) {
		const key = getCountyId(feature)
		countyFeaturesById[key] = feature
		counties.push({ name: feature.get("NAME"), state: feature.get("STUSPS"), key })
	}
	counties.sort((a, b) => a.name.localeCompare(b.name) || a.state.localeCompare(b.state))
	countyList.value = counties

	mapInstance.addLayer(countylayer)
	mapInstance.addLayer(placelayer)
	mapInstance.addLayer(listingsLayer)

	mapInstance.on('pointermove', (evt) => {
		mouseX.value = evt.originalEvent.clientX
		mouseY.value = evt.originalEvent.clientY
		const listingFeature = mapInstance.forEachFeatureAtPixel(evt.pixel, f => f, { layerFilter: l => l === listingsLayer })
		mapInstance.getViewport().style.cursor = listingFeature ? 'pointer' : ''
		if (listingFeature) {
			hoveredFeature.value = null
			isHovering.value = false
			return
		}
		const [feature, layer] = mapInstance.forEachFeatureAtPixel(evt.pixel, (f, l) => ([f, l]), { layerFilter: l => ((l === countylayer && countyActive) || (l === placelayer && cityActive))}) ?? [undefined, undefined]
		hoveredFeature.value = feature ?? null
		isHovering.value = !!feature
		isHoveringPlace.value = layer === placelayer
		if (highlightedId.value != null && isHovering.value) { highlightedId.value = null }
	})
	mapInstance.getViewport().addEventListener('mouseout', () => { isHovering.value = false })

	mapInstance.on('click', (evt) => {
		const listingFeature = mapInstance.forEachFeatureAtPixel(evt.pixel, f => f, { layerFilter: l => l === listingsLayer })
		if (listingFeature) {
			const address = listingFeature.get('address')
			if (!address) return
			addressQuery.value = address
			fetchProperty(address).catch(() => {})
		}
		else {
			const [feature, layer] = mapInstance.forEachFeatureAtPixel(evt.pixel, (f, l) => ([f, l]), { layerFilter: l => ((l === countylayer && countyActive) || (l === placelayer && cityActive))}) ?? [null, null]
			emit("triggerDetail", feature, layer === placelayer)
		}
	})

	mapInstance.on('moveend', () => {
		const view = mapInstance.getView()
		const zoom = view.getZoom()
		const show = zoom != null && zoom >= LISTINGS_MIN_ZOOM
		listingsLayer.setVisible(show)
		if (!show) return

		const center = toLonLat(view.getCenter())
		const extent = view.calculateExtent(mapInstance.getSize())
		const widthMeters = extent[2] - extent[0]
		const radiusMiles = Math.min(10, Math.max(1, (widthMeters / 2) / 1609.34))
		fetchListings(center[1], center[0], radiusMiles)
	})

	loading.value = false
})


watch(highlightedId, () => countylayer.changed())
watch(populationFilter, () => countylayer.changed())
watch(heatmapShows, () => countylayer.changed())

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

function setVisible(layer, status) {
	if (layer === "county") {
		countylayer.setVisible(status)
	}
	if (layer === "city") {
		placelayer.setVisible(status)
	}
}

function setInteractable(layer, status) {
	if (layer === "county") {
		countyActive = status
	}
	if (layer === "city") {
		cityActive = status
	}
}

defineExpose({
	mapInstance,
	OSMLayer,
	countyList,
	goToCounty,
	goToCoordinate,
	setVisible,
	setInteractable,
	heatmapShows,
	populationFilter,
})

</script>

<template>
	
	<div class="map" ref="mapRoot">
		<div id="loading" v-show="loading">
			<img src="/logo.png" width="128" height="256" style="image-rendering: pixelated; image-rendering: crisp-edges;"></img>
			<img src="/loading-9.gif" style="width: 10%; aspect-ratio: 1; object-fit: cover; "></img>
		</div>
		<div class="hover-box" v-if="isHovering && hoverInfo" :style="{ left: mouseX + 12 + 'px', top: mouseY + 20 + 'px' }">
			<h3>{{ hoverInfo.name }}, {{ hoverInfo.state }}</h3>
			<template v-if="hoverInfo.filtered"><i>Filtered: population below threshold</i><br></template>
			Price/Rent Ratio: <b>{{ hoverInfo.ratio == null ? "N/A" : hoverInfo.ratio.toFixed(2) }}</b><br>
			Median Contract Rent: $<b>{{ hoverInfo.rent == null ? "N/A" : hoverInfo.rent.toLocaleString() }}</b>/mo<br>
			Median House Price: $<b>{{ hoverInfo.houseprice == null ? "N/A" : hoverInfo.houseprice.toLocaleString() }}</b><br>
			Population: <b>{{ hoverInfo.population != null ? hoverInfo.population.toLocaleString() : 'N/A' }}</b><br>
			<template v-if="hoverInfo.score != null">Investment Score: <b>{{ hoverInfo.score.toFixed(1) }}</b></template>
			<!--<template v-else>No price/rent data</template>-->
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
#loading {
	position: fixed;
	top: 0;
	left: 0;
	z-index: 100;
	width: 100%;
	height: 100%;
	background: white;
	align-content: center;
	justify-content: center;
	align-items: center;
	flex-direction: column;
	display: flex;
}
</style>
