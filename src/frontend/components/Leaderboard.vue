<script setup>
import { computed, onMounted, ref } from 'vue'
import { useCountyScores } from '../composables/countyScores.js'

const props = defineProps({
	counties: { type: Array, default: () => [] },
})
const emit = defineEmits(['select'])

const { weights, weightsSum, weightsValid, rawCountyData, countyScores,
	ensureLoaded, resetWeights, keyFor, FACTORS, populationFilter} = useCountyScores()

onMounted(ensureLoaded)

const FACTOR_LABELS = {
	ratio: 'Price/Rent Ratio',
	apprec: 'Appreciation',
	rentGrowth: 'Rent Growth',
	tax: 'Property Tax',
	vac: 'Vacancy',
	pop: 'Population',
}
const factorKeys = Object.keys(FACTORS)

const sortKey = ref('score')
const sortDesc = ref(true)
function setSort(key) {
	if (sortKey.value === key) {
		sortDesc.value = !sortDesc.value
	} else {
		sortKey.value = key
		sortDesc.value = true
	}
}

const rows = computed(() => {
	if (!rawCountyData.value) return []
	const minPopulation = populationFilter.value
	const list = []
	for (const c of props.counties) {
		const dataKey = keyFor(c.name, c.state)
		const raw = rawCountyData.value[dataKey]
		const info = countyScores.value[dataKey]
		if (!raw || !info || info.score == null) continue
		if (minPopulation > 0 && !(raw.population >= minPopulation)) continue
		list.push({
			key: c.key,
			name: c.name,
			state: c.state,
			score: info.score,
			partialData: info.partialData,
			ratio: raw.ratio,
			rentGrowth: raw.rentGrowth,
			pop: raw.population,
		})
	}
	list.sort((a, b) => {
		const av = a[sortKey.value], bv = b[sortKey.value]
		const cmp = typeof av === 'string' ? av.localeCompare(bv) : av - bv
		return sortDesc.value ? -cmp : cmp
	})
	return list.slice(0, 25)
})

function selectRow(row) {
	emit('select', { type: 'county', key: row.key })
}
</script>

<template>

<div id="leaderboard">
	<div class="weights-panel">
		<h4>Score Weights</h4>
		<div class="weight-row" v-for="k in factorKeys" :key="k">
			<label :for="'weight-' + k">{{ FACTOR_LABELS[k] }}</label>
			<input
				:id="'weight-' + k"
				type="number"
				min="0"
				max="1"
				step="0.05"
				v-model.number="weights[k]"
			/>
		</div>
		<div class="sum-row" :class="{ invalid: !weightsValid }">
			Sum: {{ weightsSum.toFixed(2) }}
			<span v-if="!weightsValid" class="error">Each weight must be 0–1 and sum to 1.00</span>
		</div>
		<button type="button" @click="resetWeights">Reset to defaults</button>
	</div>

	<div class="filter-note" v-if="populationFilter !== 'all'">
		Showing counties with population {{ populationFilter }}+
	</div>

	<table>
		<thead>
			<tr>
				<th>Rank</th>
				<th @click="setSort('name')" :class="{ active: sortKey === 'name' }">County</th>
				<th @click="setSort('state')" :class="{ active: sortKey === 'state' }">State</th>
				<th @click="setSort('score')" :class="{ active: sortKey === 'score' }">Score</th>
				<th @click="setSort('ratio')" :class="{ active: sortKey === 'ratio' }">Ratio</th>
				<th @click="setSort('rentGrowth')" :class="{ active: sortKey === 'rentGrowth' }">Rent&nbsp;Growth</th>
				<th @click="setSort('pop')" :class="{ active: sortKey === 'pop' }">Population</th>>
			</tr>
		</thead>
		<tbody>
			<tr v-for="(row, i) in rows" :key="row.key" @click="selectRow(row)">
				<td class="rank">{{ i + 1 }}</td>
				<td>{{ row.name }}<span v-if="row.partialData" title="Partial data">*</span></td>
				<td>{{ row.state }}</td>
				<td>{{ row.score.toFixed(1) }}</td>
				<td>{{ row.ratio == null ? 'N/A' : row.ratio.toFixed(2) }}</td>
				<td>{{ row.rentGrowth == null ? 'N/A' : (row.rentGrowth * 100).toFixed(1) + '%' }}</td>
				<td>{{ row.pop == null ? 'N/A' : row.pop.toLocaleString() }}</td>
			</tr>
		</tbody>
	</table>
</div>
</template>

<style scoped>
#leaderboard {
	position: fixed;
	margin-left: 16px;
	scrollbar-width: none;
	flex: auto;
	max-height: calc(100%);
	z-index: 100;
	right: 0px;
	padding: 16px;
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	border: var(--overlay-border);
	border-radius: 16px;
	overflow-y: auto;
	font: 13px Arial, sans-serif;
	pointer-events: auto;
}
#leaderboard h4 {
	margin: 0 0 8px;
	color: #777;
}
.weights-panel {
	display: flex;
	flex-direction: column;
	gap: 4px;
	margin-bottom: 12px;
	padding-bottom: 12px;
	border-bottom: var(--overlay-border)
}
.weight-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 8px;
	font: 12px Arial, sans-serif;
	color: #333;
}
.weight-row input {
	width: 60px;
	font: 12px Arial, sans-serif;
	border: var(--overlay-border);
	border-radius: 4px;
	padding: 2px 4px;
	outline: none;
	background: white;
}
.weight-row input:focus {
	border-color: #666;
}
.sum-row {
	font: 12px Arial, sans-serif;
	font-weight: bold;
	color: #333;
	margin-top: 4px;
}
.sum-row.invalid {
	color: #c0392b;
}
.sum-row .error {
	display: block;
	font: 11px Arial, sans-serif;
	font-weight: normal;
	color: #c0392b;
}
.weights-panel button {
	align-self: flex-start;
	margin-top: 6px;
	font: 12px Arial, sans-serif;
	padding: 4px 8px;
	border: var(--overlay-border);
	border-radius: 6px;
	background: white;
	cursor: pointer;
}
.weights-panel button:hover {
	border-color: #666;
}
.filter-note {
	font: 11px Arial, sans-serif;
	color: #777;
	margin-bottom: 6px;
}
table {
	width: 100%;
	border-collapse: collapse;
}
th {
	position: sticky;
	top: 0;
	background: rgba(255, 255, 255, 0.9);
	text-align: left;
	padding: 4px 6px;
	font-size: 12px;
	color: #555;
	cursor: pointer;
	user-select: none;
	white-space: nowrap;
}
th:hover {
	color: #000;
}
th.active {
	color: #000;
	font-weight: bold;
}
tbody tr {
	cursor: pointer;
}
tbody tr:hover {
	background: #f5f5f5;
}
td {
	padding: 4px 6px;
	border-top: 1px solid #eee;
}
td.rank {
	color: #999;
}
</style>
