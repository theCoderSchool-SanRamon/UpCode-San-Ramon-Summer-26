<script setup>
import { onMounted, ref, watch} from 'vue'

const searchQuery = ref("")
const searchSuggestions = ref([])
const suggestionDebounceTimer = ref(null)
/*
watch()
					searchQuery(val)
						if (this.searchMode=='city') {
							clearTimeout(this.suggestionDebounceTimer);
							if (!val.trim()) { this.searchSuggestions = []; return; }
							this.suggestionDebounceTimer = setTimeout(() => this.fetchCities(val), 350);
						} else if (this.searchMode=='zip') {
							clearTimeout(this.suggestionDebounceTimer);
							if (!val.trim()) { this.searchSuggestions = []; return; }
							this.suggestionDebounceTimer = setTimeout(() => this.fetchZIP(val), 350);
						}
*/
</script>

<template>

<div id="search-wrapper">
	<input
	class="search-input"
	type="text"
	v-model="searchQuery"
	placeholder="Search for a place..."
	autocomplete="off"
	/>
	<Transition>
	<ul class="suggestions" v-if="searchQuery.length > 0">
					<li
						v-for="place in suggestions"
						:key="place.key"
						@mousedown.prevent="zoomTo(place)"
					>
						{{ place.name }}, {{ place.state }}
					</li>
				</ul>
	</Transition>
</div>
</template>

<style scoped>
#search-wrapper {
	min-width: 16px;
	min-height: 16px;
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
</style>