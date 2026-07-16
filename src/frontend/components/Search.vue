<script setup>
import { computed, ref, watch, nextTick } from 'vue'

const props = defineProps({
	counties: { type: Array, default: () => [] },
})
const emit = defineEmits(['select'])

const searchMode = ref('county')
const searchActive = ref(false)
const searchQuery = ref('')
const searchInputEntry = ref(null)
const searchSuggestions = ref([])
let suggestionDebounceTimer = null

const isOnlyDigits = (str) => /^\d+$/.test(str);

watch(searchQuery, (val) => {
	clearTimeout(suggestionDebounceTimer)
	if (!val.trim()) { searchSuggestions.value = []; return }
	if (isOnlyDigits(val)) {
		suggestionDebounceTimer = setTimeout(() => fetchZIP(val), 350)
	} else { suggestionDebounceTimer = setTimeout(() => fetchSearch(val), 350) }
	/*
	if (isOnlyDigits(val)) {
		suggestionDebounceTimer = setTimeout(() => fetchZIP(val), 350)
	} else if (searchMode.value === 'city/zip') {
		suggestionDebounceTimer = setTimeout(() => fetchCities(val), 350)
	}*/
	
})

watch (searchMode, () => {
	searchInputEntry.value.focus()
})


const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function handleBlur(event) {
	searchQuery.value = ''
	searchSuggestions.value = []
	await wait(200)
	searchActive.value = false
}

function selectCounty(county) {
	emit('select', { type: 'county', key: county.key })
	searchQuery.value = ''
}
async function fetchSearch(query) {

	try {
		const url = `https://photon.komoot.io/api/?q=${encodeURIComponent(query)}&limit=12&countrycode=US&dedupe=1`
		const res = await fetch(url, { headers: { 'Accept-Language': 'en' } })
		const data = await res.json()
		console.log(data.features)
		const cityTypes = ['city', 'town', 'village', 'hamlet', 'municipality', 'borough']
		searchSuggestions.value = data.features
			.filter(r => {
				return !(["house","street","district"].includes(r.properties.type))
			})
			.map(r => {
				const display = []
				if (r.properties.name) {display.push(r.properties.name + (r.properties.osm_value==="county"&&!r.properties.name.toLowerCase().includes("county") ? " County" : ""))}
				if (r.properties.city && r.properties.city != r.properties.name) {display.push(r.properties.city)}
				if (r.properties.state) {display.push(r.properties.state)}
				return { restype: 'city', key: r.properties.osm_id, place_id: r.properties.osm_id, display: display.join(", "), lat: parseFloat(r.geometry.coordinates[1]), lon: parseFloat(r.geometry.coordinates[0]) }
			})
	} catch (e) {
		console.log(e)
		searchSuggestions.value = []
	}
}
async function fetchCities(query) {
	try {
		const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=8&countrycodes=us&addressdetails=1`
		const res = await fetch(url, { headers: { 'Accept-Language': 'en' } })
		const data = await res.json()
		const cityTypes = ['city', 'town', 'village', 'hamlet', 'municipality', 'borough']
		searchSuggestions.value = data
			.filter(r => {
				const hasCoords = r.lat && r.lon
				const isCity = cityTypes.includes(r.addresstype) || cityTypes.includes(r.type)
				return hasCoords && isCity
			})
			.map(r => {
				const addr = r.address || {}
				const city = addr.city || addr.town || addr.village || addr.municipality || r.name
				const state = addr.state || ''
				return { restype: 'city', key: r.place_id, place_id: r.place_id, display: state ? `${city}, ${state}` : city, lat: parseFloat(r.lat), lon: parseFloat(r.lon) }
			})
	} catch (e) {
		searchSuggestions.value = []
	}
}
function selectCity(city) {
	emit('select', { type: 'point', lon: city.lon, lat: city.lat })
	searchQuery.value = ''
	searchSuggestions.value = []
}

function selectResult(res) {
	if (res.restype == 'city') {
		selectCity(res)
	} else if (res.restype == 'zip') {
		selectZIP(res)
	} else {
		selectCounty(res)
	}
}

async function fetchZIP(query) {
	try {
		const url = `https://api.zippopotam.us/us/${encodeURIComponent(query)}`
		const res = await fetch(url, { headers: { 'Accept-Language': 'en' } })
		const data = await res.json()
		const place = data['places'][0]
		searchSuggestions.value = [{ restype: 'zip', key: `${place['place name']}, ${place['state']}`, display: `${place['place name']}, ${place['state']}`, lat: parseFloat(place.latitude), lon: parseFloat(place.longitude) }]
	} catch (e) {
		searchSuggestions.value = []
	}
}
function selectZIP(zip) {
	emit('select', { type: 'point', lon: zip.lon, lat: zip.lat })
	searchQuery.value = ''
	searchSuggestions.value = []
}

async function onSearchButton() {
	searchActive.value=!searchActive.value
	if (searchActive.value) {
		await nextTick()
		searchInputEntry.value.focus()
	}
}

</script>

<template>
<div id="search-container">
	<button id="search-button" v-if="!searchActive" @click="onSearchButton()">
		<img src="/250px-Search_Icon.svg.png" class="img-icon"></img>
	</button>
	<div id="search-wrapper" v-if="searchActive">
		<Transition name="search">
		<input
			id="search-input"
			ref="searchInputEntry"
			type="text"
			placeholder="Search for a place..."
			v-model="searchQuery"
			v-if="searchActive"
			@blur="handleBlur"
			autocomplete="off"
		/>
		</Transition>
		<Transition>
		<ul class="suggestions" v-if="searchSuggestions.length > 0">
			<li
				v-for="opt in searchSuggestions"
				:key="opt.key"
				@mousedown.prevent="selectResult(opt)"
			>
				{{ opt.display }}
			</li>
		</ul>
		</Transition>


	</div>
</div>
</template>

<style scoped>

.v-enter-active, .v-leave-active {
	transition: opacity 0.5s ease;
}
.v-enter-from, .v-leave-to {
	opacity: 0;
}

.search-enter-active, .search-leave-active {
	transition: width 0.2s ease;
}
.search-enter-from, .search-leave-to {
	width: 32px;
}

.img-icon {
	width: 20px;
	height: 20px;
	object-fit: contain;
}

#search-button {
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	border: var(--overlay-border);
	border-radius: 14px;
	width: 32px;
	height: 32px;
	padding: 8px 10px;
	outline: none;
	margin: 16px;
	pointer-events: auto;
	font: 24px Arial, sans-serif;
	text-align: center;
	justify-content: center;
	align-items: center;
	min-width: 16px;
	min-height: 16px;
	display: inline-flex;
	gap: 6px;
	cursor: pointer;
}
#search-wrapper {
	min-width: 16px;
	min-height: 16px;
	display: flex;
	flex-direction: column;
	gap: 6px;
}
#search-input {
	width: 32px;
	height: 32px;
	margin: 16px;
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	padding: 8px 10px;
	font: 14px Arial, sans-serif;
	border: var(--overlay-border);
	border-radius: 14px;
	outline: none;
	pointer-events: auto;
	transition: width 0.2s ease-in-out;
}
#search-input:focus, #search-input.fakefocus {
	width: 25%;
}
#mode-select {
	margin-left: 16px;
	width: fit-content;
	font: 13px Arial, sans-serif;
	border: var(--overlay-border);
	border-radius: 8px;
	outline: none;
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	padding: 4px 8px;
	cursor: pointer;
	pointer-events: auto;
}
#mode-select:focus {
	border-color: #666;
}
.suggestions {
	list-style: none;
	max-height: calc(100vh - 140px);
	max-width: 25%;
	margin-left: 16px;
	overflow-y: auto;
	border-radius: 4px;
	background: transparent;
	pointer-events: auto;
}
.suggestions li {
	padding: 8px 10px;
	font: 13px Arial, sans-serif;
	cursor: pointer;
	border-radius: 4px;
	margin: 2px;
	background: rgba(255, 255, 255, 0.666);
	backdrop-filter: blur(3px);
	border: 0.5px solid #f0f0f0;
	color: #333;
	transition: margin 0.2s ease-in-out;
}
.suggestions li:hover {
	background-color: #f5f5f5;
	margin-left: 4px;
}
</style>
