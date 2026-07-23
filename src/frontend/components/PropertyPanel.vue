<script setup>
import { computed, ref, watch } from 'vue'
import { usePropertyAnalysis } from '../composables/propertyAnalysis.js'
import { getStreetviewPhoto, streetviewImageUrl } from '../composables/streetview.js'

const {
	assumptions, currentProperty, compareList, loading, error, MAX_COMPARE,
	addToCompare, resetAssumptions, computeMetrics, computePropertyScore, countyContext,
} = usePropertyAnalysis()

function closePanel() {
	currentProperty.value = null
}

const photoUrl = ref(undefined) // undefined = loading/none, null = unavailable, string = image url
let photoRequestToken = 0

watch(currentProperty, (property) => {
	photoUrl.value = undefined
	if (!property || property.latitude == null || property.longitude == null) {
		photoUrl.value = null
		return
	}
	const { latitude: lat, longitude: lng, address } = property
	const token = ++photoRequestToken
	getStreetviewPhoto(address, lat, lng).then(url => {
		if (token !== photoRequestToken) return
		photoUrl.value = url ? streetviewImageUrl(lat, lng, '600x450') : null
	})
}, { immediate: true })

const metrics = computed(() => computeMetrics(currentProperty.value))
const investmentScore = computed(() => computePropertyScore(metrics.value))
const context = computed(() => countyContext(currentProperty.value))

function scoreColor(score) {
	if (score == null) return '#999'
	const pct = Math.min(Math.max(score, 0), 100)
	return pct < 50
		? `color-mix(in srgb, red, yellow ${pct * 2}%)`
		: `color-mix(in srgb, yellow, green ${(pct - 50) * 2}%)`
}

const alreadyCompared = computed(() =>
	!!currentProperty.value && compareList.value.some(p => p.id === currentProperty.value.id)
)
const compareFull = computed(() => compareList.value.length >= MAX_COMPARE && !alreadyCompared.value)

function fmtDollar(v) {
	if (v == null || Number.isNaN(v)) return '—'
	const sign = v < 0 ? '-' : ''
	return sign + '$' + Math.round(Math.abs(v)).toLocaleString('en-US')
}
function fmtPercent(v) {
	if (v == null || Number.isNaN(v) || !Number.isFinite(v)) return '—'
	return (v * 100).toFixed(1) + '%'
}
function fmtRatio(v) {
	if (v == null || Number.isNaN(v) || !Number.isFinite(v)) return '—'
	return v.toFixed(2) + '×'
}

const METRICS_META = [
	{ key: 'grossYield', label: 'Gross Yield', format: fmtPercent,
		caption: 'Annual rent as a share of purchase price, before expenses.' },
	{ key: 'NOI', label: 'NOI (annual)', format: fmtDollar,
		caption: 'Rent left after vacancy, management, maintenance, tax, and insurance before the mortgage.' },
	{ key: 'capRate', label: 'Cap Rate', format: fmtPercent,
		caption: 'NOI as a share of price the return if you paid all cash.' },
	{ key: 'monthlyMortgage', label: 'Monthly Mortgage', format: fmtDollar,
		caption: 'Principal + interest payment on the financed amount.' },
	{ key: 'monthlyCashFlow', label: 'Monthly Cash Flow', format: fmtDollar,
		caption: "What's left over each month after expenses and the mortgage." },
	{ key: 'cashOnCash', label: 'Cash on Cash', format: fmtPercent,
		caption: 'Annual cash flow as a share of the cash you put in (down payment + closing costs).' },
	{ key: 'DSCR', label: 'DSCR', format: fmtRatio,
		caption: 'NOI divided by annual mortgage payments; lenders typically want 1.20×+.' },
]
</script>

<template>

<div id="property-lookup">
	<div class="lookup-status" v-if="loading">Looking up property…</div>
	<div class="lookup-status error" v-else-if="error">{{ error }}</div>

	<div class="property-row" v-if="currentProperty">
	<div class="property-panel">
		<div class="panel-header">
			<h3>{{ currentProperty.address }}</h3>
			<button type="button" class="close-btn" @click="closePanel">&times;</button>
		</div>

		<div class="facts-row">
			<span>{{ currentProperty.beds ?? '—' }} bd</span>
			<span>{{ currentProperty.baths ?? '—' }} ba</span>
			<span>{{ currentProperty.sqft ? currentProperty.sqft.toLocaleString() : '—' }} sqft</span>
			<span>Built {{ currentProperty.yearBuilt ?? '—' }}</span>
			<span class="score-badge" :style="{ color: scoreColor(investmentScore?.score) }">
				Score: {{ investmentScore?.score ?? '—' }}
			</span>
		</div>

		<div class="county-strip" v-if="context">
			<h4>{{ currentProperty.county }}, {{ currentProperty.state }}</h4>
			<span>Score: <b>{{ context.score != null ? context.score.toFixed(1) : '—' }}</b></span>
			<span>Ratio: <b>{{ context.raw.ratio != null ? context.raw.ratio.toFixed(2) : '—' }}</b></span>
			<span>Rent Growth: <b>{{ context.raw.rentGrowth != null ? (context.raw.rentGrowth * 100).toFixed(1) + '%' : '—' }}</b></span>
			<span>Vacancy: <b>{{ context.raw.vac != null ? (context.raw.vac * 100).toFixed(1) + '%' : '—' }}</b></span>
		</div>
		<div class="county-strip muted" v-else>
			County context unavailable for this location.
		</div>

		<div class="field-grid">
			<label>Estimated Value ($)
				<input type="number" min="0" step="1000" v-model.number="currentProperty.price" />
			</label>
			<label>Estimated Rent ($/mo)
				<input type="number" min="0" step="10" v-model.number="currentProperty.rent" />
			</label>
		</div>

		<details class="assumptions" open>
			<summary>Assumptions</summary>
			<div class="field-grid">
				<label>Down Payment (%)
					<input type="number" min="0" max="100" step="1" v-model.number="assumptions.downPaymentPct" />
				</label>
				<label>Mortgage Rate (%)
					<input type="number" min="0" max="20" step="0.1" v-model.number="assumptions.mortgageRatePct" />
				</label>
				<label>Term (yrs)
					<input type="number" min="1" max="40" step="1" v-model.number="assumptions.termYears" />
				</label>
				<label>Vacancy (%)
					<input type="number" min="0" max="100" step="1" v-model.number="assumptions.vacancyPct" />
				</label>
				<label>Management (% rent)
					<input type="number" min="0" max="100" step="1" v-model.number="assumptions.managementPct" />
				</label>
				<label>Maintenance (% rent)
					<input type="number" min="0" max="100" step="1" v-model.number="assumptions.maintenancePct" />
				</label>
				<label>Closing Costs (%)
					<input type="number" min="0" max="100" step="0.5" v-model.number="assumptions.closingCostPct" />
				</label>
				<label>Property Tax ($/yr)
					<input type="number" min="0" step="50" v-model.number="currentProperty.propertyTaxAnnual" />
				</label>
				<label>Insurance ($/yr)
					<input type="number" min="0" step="50" v-model.number="currentProperty.insuranceAnnual" />
				</label>
			</div>
			<div class="tax-source" v-if="currentProperty.propertyTaxAnnual != null">
				Tax source: {{ currentProperty.propertyTaxFromRentCast ? 'RentCast tax history' : (context ? 'county effective rate' : 'manual') }}
			</div>
			<button type="button" @click="resetAssumptions">Reset assumptions</button>
		</details>

		<div class="metrics" v-if="metrics">
			<div class="metric-row" v-for="m in METRICS_META" :key="m.key">
				<div class="metric-value">
					<span class="metric-label">{{ m.label }}</span>
					<span class="metric-number">{{ m.format(metrics[m.key]) }}</span>
				</div>
				<div class="metric-caption">{{ m.caption }}</div>
			</div>
		</div>

		<button
			type="button"
			class="compare-btn"
			:disabled="alreadyCompared || compareFull"
			@click="addToCompare(currentProperty)"
		>
			{{ alreadyCompared ? 'Added to Compare' : compareFull ? 'Compare full (4 max)' : 'Add to Compare' }}
		</button>
	</div>

	<div class="property-photo-panel">
		<img v-if="photoUrl" :src="photoUrl" alt="" />
		<div v-else class="property-photo-placeholder"></div>
	</div>
	</div>
</div>
</template>

<style scoped>

#property-lookup {
	display: flex;
	flex-direction: column;
	pointer-events: none;
	width: 100%;
	min-width: 64px;
	margin-top: 64px;
}
.lookup-status {
	margin: 0 16px 16px;
	font: 12px Arial, sans-serif;
	color: #777;
	pointer-events: none;
}
.lookup-status.error {
	color: #c0392b;
}
.property-row {
	display: flex;
	flex-direction: row;
	align-items: flex-start;
	gap: 12px;
}
.property-photo-panel {
	pointer-events: auto;
	flex-shrink: 0;
	width: 320px;
	height: 260px;
	margin: 0 0 16px 0;
	border-radius: 12px;
	overflow: hidden;
	box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
	background: #ccc;
}
.property-photo-panel img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	display: block;
}
.property-photo-placeholder {
	width: 100%;
	height: 100%;
	background: #ccc;
}
.property-panel {
	pointer-events: auto;
	width: 340px;
	max-height: calc(100vh - 100px);
	margin: 0 0 16px 16px;
	padding: 16px;
	background: var(--overlay-background);
	backdrop-filter: blur(5px);
	box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
	border-radius: 8px;
	overflow-y: auto;
	font: 13px Arial, sans-serif;
	color: #333;
}
.panel-header {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	gap: 8px;
	margin-bottom: 8px;
}
.panel-header h3 {
	font-size: 14px;
	line-height: 1.3;
}
.close-btn {
	flex: none;
	border: none;
	background: none;
	font-size: 18px;
	line-height: 1;
	cursor: pointer;
	color: #777;
	padding: 0 2px;
}
.close-btn:hover {
	color: #000;
}
.facts-row {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
	font-size: 12px;
	color: #555;
	margin-bottom: 12px;
	padding-bottom: 12px;
	border-bottom: 1px solid #ccc;
}
.score-badge {
	margin-left: auto;
	font-weight: bold;
}
.county-strip {
	display: flex;
	flex-wrap: wrap;
	gap: 8px 12px;
	align-items: baseline;
	font-size: 12px;
	color: #333;
	margin-bottom: 12px;
	padding-bottom: 12px;
	border-bottom: 1px solid #ccc;
}
.county-strip h4 {
	flex-basis: 100%;
	font-size: 12px;
	color: #777;
	font-weight: normal;
}
.county-strip.muted {
	color: #999;
	font-style: italic;
}
.field-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 8px;
	margin-bottom: 8px;
}
.field-grid label {
	display: flex;
	flex-direction: column;
	gap: 2px;
	font-size: 11px;
	color: #555;
}
.field-grid input {
	font: 12px Arial, sans-serif;
	border: 1px solid #ccc;
	border-radius: 4px;
	padding: 4px 6px;
	outline: none;
	background: white;
}
.field-grid input:focus {
	border-color: #666;
}
.assumptions {
	margin: 8px 0 12px;
	padding-bottom: 12px;
	border-bottom: 1px solid #ccc;
}
.assumptions summary {
	cursor: pointer;
	font-size: 12px;
	font-weight: bold;
	color: #777;
	margin-bottom: 8px;
}
.tax-source {
	font-size: 11px;
	color: #999;
	margin-bottom: 6px;
}
.assumptions button,
.compare-btn {
	font: 12px Arial, sans-serif;
	padding: 6px 10px;
	border: 1px solid #ccc;
	border-radius: 6px;
	background: white;
	cursor: pointer;
}
.assumptions button:hover,
.compare-btn:hover:not(:disabled) {
	border-color: #666;
}
.metrics {
	display: flex;
	flex-direction: column;
	gap: 10px;
	margin-bottom: 14px;
}
.metric-value {
	display: flex;
	justify-content: space-between;
	align-items: baseline;
}
.metric-label {
	color: #555;
}
.metric-number {
	font-weight: bold;
	font-size: 14px;
}
.metric-caption {
	font-size: 11px;
	color: #888;
	margin-top: 1px;
}
.compare-btn {
	width: 100%;
	font-weight: bold;
}
.compare-btn:disabled {
	color: #999;
	cursor: default;
}
</style>
