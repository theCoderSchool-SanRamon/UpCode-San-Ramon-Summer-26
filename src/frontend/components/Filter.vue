<script setup>
import ToolDropdown from './ToolDropdown.vue'
import { useCountyScores } from '../composables/countyScores.js'

const {populationFilter} = useCountyScores()
</script>

<template>
<ToolDropdown :icon-closed="'/107799.png'">
	<div class="filter-body">
		<div class="population-filter">
			<p><b>Filter by County Population</b></p>
			<div class="population-filter-slider-and-text"> <input type="range" v-model="populationFilter" min="0" max="1000000"> </input> ≥ {{Number(populationFilter).toLocaleString()}} </div>
		</div>
	</div>
</ToolDropdown>
</template>

<style scoped>
.population-filter-slider-and-text {
	display: inline-flex;
	gap: 8px;
	width: 100%;
}
.population-filter p {
	margin-bottom: 4px;
}
.filter-body {
	pointer-events: auto;
	margin: 16px;
	padding: 8px 10px;
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
	border-radius: 8px;
	overflow-y: auto;
	font: 13px Arial, sans-serif;
	border: var(--overlay-border);
	outline: none;
}
</style>
