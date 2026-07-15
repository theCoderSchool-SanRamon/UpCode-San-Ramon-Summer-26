<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
	counties: { type: Array, default: () => [] },
})
const emit = defineEmits(['select'])

const searchMode = ref('county')
const searchQuery = ref('')
const searchSuggestions = ref([])
let suggestionDebounceTimer = null

const filteredCounties = computed(() => {
	const q = searchQuery.value.toLowerCase()
	if (!q) return []
	const startsWith = []
	const includes = []
	for (const c of props.counties) {
		const nameLower = c.name.toLowerCase()
		const fullLower = nameLower + ', ' + c.state.toLowerCase()
		if (nameLower.startsWith(q)) {
			startsWith.push(c)
		} else if (fullLower.includes(q)) {
			includes.push(c)
		}
	}
	return [...startsWith, ...includes].slice(0, 12)
})

watch(searchQuery, (val) => {
	if (searchMode.value === 'city') {
		clearTimeout(suggestionDebounceTimer)
		if (!val.trim()) { searchSuggestions.value = []; return }
		suggestionDebounceTimer = setTimeout(() => fetchCities(val), 350)
	} else if (searchMode.value === 'zip') {
		clearTimeout(suggestionDebounceTimer)
		if (!val.trim()) { searchSuggestions.value = []; return }
		suggestionDebounceTimer = setTimeout(() => fetchZIP(val), 350)
	}
})

function handleBlur() {
	searchQuery.value = ''
}
function handleCityBlur() {
	searchQuery.value = ''
	searchSuggestions.value = []
}
function handleZIPBlur() {
	searchQuery.value = ''
	searchSuggestions.value = []
}

function selectCounty(county) {
	emit('select', { type: 'county', key: county.key })
	searchQuery.value = ''
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
				return { place_id: r.place_id, display: state ? `${city}, ${state}` : city, lat: parseFloat(r.lat), lon: parseFloat(r.lon) }
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

async function fetchZIP(query) {
	try {
		const url = `https://api.zippopotam.us/us/${encodeURIComponent(query)}`
		const res = await fetch(url, { headers: { 'Accept-Language': 'en' } })
		const data = await res.json()
		const place = data['places'][0]
		searchSuggestions.value = [{ display: `${place['place name']}, ${place['state']}`, lat: parseFloat(place.latitude), lon: parseFloat(place.longitude) }]
	} catch (e) {
		searchSuggestions.value = []
	}
}
function selectZIP(zip) {
	emit('select', { type: 'point', lon: zip.lon, lat: zip.lat })
	searchQuery.value = ''
	searchSuggestions.value = []
}
</script>

<template>

<div id="search-wrapper">
	<input
		v-if="searchMode === 'county'"
		class="search-input"
		type="text"
		placeholder="Search county..."
		v-model="searchQuery"
		@blur="handleBlur"
		autocomplete="off"
	/>
	<Transition>
	<ul class="suggestions" v-if="searchMode === 'county' && searchQuery.length > 0 && filteredCounties.length > 0">
		<li
			v-for="county in filteredCounties"
			:key="county.key"
			@mousedown.prevent="selectCounty(county)"
		>
			{{ county.name }}, {{ county.state }}
		</li>
	</ul>
	</Transition>

	<input
		v-if="searchMode === 'city'"
		class="search-input"
		type="text"
		placeholder="Search city..."
		v-model="searchQuery"
		@blur="handleCityBlur"
		autocomplete="off"
	/>
	<Transition>
	<ul class="suggestions" v-if="searchMode === 'city' && searchSuggestions.length > 0">
		<li
			v-for="city in searchSuggestions"
			:key="city.place_id"
			@mousedown.prevent="selectCity(city)"
		>
			{{ city.display }}
		</li>
	</ul>
	</Transition>

	<input
		v-if="searchMode === 'zip'"
		class="search-input"
		type="text"
		placeholder="Search ZIP code..."
		v-model="searchQuery"
		@blur="handleZIPBlur"
		autocomplete="off"
	/>
	<Transition>
	<ul class="suggestions" v-if="searchMode === 'zip' && searchSuggestions.length > 0">
		<li
			v-for="zip in searchSuggestions"
			:key="zip.display"
			@mousedown.prevent="selectZIP(zip)"
		>
			{{ zip.display }}
		</li>
	</ul>
	</Transition>

	<select id="mode-select" v-model="searchMode">
		<option value="county">Search by County</option>
		<option value="city">Search by City</option>
		<option value="zip">Search by ZIP code</option>
	</select>
</div>
</template>

<style scoped>
#search-wrapper {
	min-width: 16px;
	min-height: 16px;
	display: flex;
	flex-direction: column;
	gap: 6px;
}
.search-input {
	width: 25%;
	margin: 16px;
	background: var(--overlay-background);
	backdrop-filter: blur(5px);
	padding: 8px 10px;
	font: 14px Arial, sans-serif;
	border: 1px solid #ccc;
	border-radius: 14px;
	outline: none;
	pointer-events: auto;
}
.search-input:focus {
	border-color: #666;
}
#mode-select {
	margin-left: 16px;
	width: fit-content;
	font: 13px Arial, sans-serif;
	border: 1px solid #ccc;
	border-radius: 8px;
	outline: none;
	background: var(--overlay-background);
	backdrop-filter: blur(5px);
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
