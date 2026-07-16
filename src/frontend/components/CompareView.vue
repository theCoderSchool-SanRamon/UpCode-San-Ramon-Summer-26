<script setup>
import { computed, ref } from 'vue'
import { usePropertyAnalysis } from '../composables/propertyAnalysis.js'

const { compareList, removeFromCompare, clearCompare, computeMetrics } = usePropertyAnalysis()

const showModal = ref(false)

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
	{ key: 'grossYield', label: 'Gross Yield', format: fmtPercent, direction: 'high' },
	{ key: 'NOI', label: 'NOI (annual)', format: fmtDollar, direction: 'high' },
	{ key: 'capRate', label: 'Cap Rate', format: fmtPercent, direction: 'high' },
	{ key: 'monthlyMortgage', label: 'Monthly Mortgage', format: fmtDollar, direction: 'low' },
	{ key: 'monthlyCashFlow', label: 'Monthly Cash Flow', format: fmtDollar, direction: 'high' },
	{ key: 'cashOnCash', label: 'Cash-on-Cash', format: fmtPercent, direction: 'high' },
	{ key: 'DSCR', label: 'DSCR', format: fmtRatio, direction: 'high' },
]

const rows = computed(() =>
	compareList.value.map((property, i) => ({
		property,
		label: `Property ${String.fromCharCode(65 + i)}`,
		metrics: computeMetrics(property),
	}))
)

function bestValueFor(key, direction) {
	const vals = rows.value.map(r => r.metrics[key]).filter(v => v != null && Number.isFinite(v))
	if (!vals.length) return null
	return direction === 'low' ? Math.min(...vals) : Math.max(...vals)
}

function isBest(row, key, direction) {
	const best = bestValueFor(key, direction)
	const v = row.metrics[key]
	return best != null && v != null && Math.abs(v - best) < 1e-6
}

const verdict = computed(() => {
	const withCashFlow = rows.value.filter(r => r.metrics.monthlyCashFlow != null)
	if (withCashFlow.length < 2) return null
	const byCashFlow = [...withCashFlow].sort((a, b) => b.metrics.monthlyCashFlow - a.metrics.monthlyCashFlow)
	const leader = byCashFlow[0]
	const runnerUp = byCashFlow[1]
	const gap = Math.round(leader.metrics.monthlyCashFlow - runnerUp.metrics.monthlyCashFlow)
	let text = `${leader.label} cash-flows ${fmtDollar(gap)}/mo more than ${runnerUp.label}.`

	const withCapRate = rows.value.filter(r => r.metrics.capRate != null)
	if (withCapRate.length >= 2) {
		const capLeader = [...withCapRate].sort((a, b) => b.metrics.capRate - a.metrics.capRate)[0]
		if (capLeader.property.id !== leader.property.id) {
			text += ` ${capLeader.label} has the best cap rate instead.`
		}
	}
	return text
})
</script>

<template>

<div id="compare-tray" v-if="compareList.length">
	<div class="chip" v-for="(row, i) in rows" :key="row.property.id">
		<span class="chip-label">{{ row.label }}</span>
		<span class="chip-address">{{ row.property.address }}</span>
		<button type="button" class="chip-remove" @click="removeFromCompare(row.property.id)">&times;</button>
	</div>
	<button type="button" class="compare-open-btn" :disabled="compareList.length < 2" @click="showModal = true">
		Compare ({{ compareList.length }})
	</button>
	<button type="button" class="clear-btn" @click="clearCompare">Clear</button>
</div>

<div id="compare-modal-backdrop" v-if="showModal" @click.self="showModal = false">
	<div class="compare-modal">
		<div class="modal-header">
			<h3>Compare Properties</h3>
			<button type="button" class="close-btn" @click="showModal = false">&times;</button>
		</div>
		<p class="verdict" v-if="verdict">{{ verdict }}</p>
		<div class="table-wrap">
			<table>
				<thead>
					<tr>
						<th class="row-label"></th>
						<th v-for="row in rows" :key="row.property.id">
							<div class="col-label">{{ row.label }}</div>
							<div class="col-address">{{ row.property.address }}</div>
						</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="m in METRICS_META" :key="m.key">
						<td class="row-label">{{ m.label }}</td>
						<td
							v-for="row in rows"
							:key="row.property.id"
							:class="{ best: isBest(row, m.key, m.direction) }"
						>
							{{ m.format(row.metrics[m.key]) }}
						</td>
					</tr>
				</tbody>
			</table>
		</div>
	</div>
</div>

</template>

<style scoped>
#compare-tray {
	position: fixed;
	bottom: 16px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 100;
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 8px;
	max-width: calc(100% - 32px);
	padding: 10px 14px;
	background: var(--overlay-background);
	backdrop-filter: blur(5px);
	box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
	border-radius: 12px;
	font: 13px Arial, sans-serif;
	pointer-events: auto;
}
.chip {
	display: flex;
	align-items: center;
	gap: 6px;
	background: rgba(255, 255, 255, 0.666);
	border: 0.5px solid #f0f0f0;
	border-radius: 8px;
	padding: 4px 8px;
	max-width: 220px;
}
.chip-label {
	font-weight: bold;
	color: #333;
	white-space: nowrap;
}
.chip-address {
	color: #666;
	font-size: 11px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
.chip-remove {
	border: none;
	background: none;
	cursor: pointer;
	color: #999;
	font-size: 14px;
	line-height: 1;
	padding: 0 2px;
}
.chip-remove:hover {
	color: #c0392b;
}
.compare-open-btn,
.clear-btn {
	font: 12px Arial, sans-serif;
	font-weight: bold;
	padding: 6px 10px;
	border: 1px solid #ccc;
	border-radius: 6px;
	background: white;
	cursor: pointer;
	white-space: nowrap;
}
.compare-open-btn:hover:not(:disabled),
.clear-btn:hover {
	border-color: #666;
}
.compare-open-btn:disabled {
	color: #999;
	cursor: default;
}

#compare-modal-backdrop {
	position: fixed;
	inset: 0;
	z-index: 200;
	background: rgba(0, 0, 0, 0.35);
	display: flex;
	align-items: center;
	justify-content: center;
	pointer-events: auto;
}
.compare-modal {
	width: min(90vw, 900px);
	max-height: 85vh;
	display: flex;
	flex-direction: column;
	background: var(--overlay-background);
	backdrop-filter: blur(12px);
	box-shadow: 0 0 30px rgba(0, 0, 0, 0.3);
	border-radius: 12px;
	padding: 20px;
	font: 13px Arial, sans-serif;
	color: #333;
}
.modal-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 8px;
}
.modal-header h3 {
	font-size: 16px;
}
.close-btn {
	border: none;
	background: none;
	font-size: 20px;
	line-height: 1;
	cursor: pointer;
	color: #777;
}
.close-btn:hover {
	color: #000;
}
.verdict {
	font-weight: bold;
	color: #2e7d32;
	margin-bottom: 14px;
}
.table-wrap {
	overflow: auto;
}
table {
	width: 100%;
	border-collapse: collapse;
}
th, td {
	padding: 8px 10px;
	text-align: left;
	border-bottom: 1px solid #ddd;
	white-space: nowrap;
}
th.row-label, td.row-label {
	color: #555;
	font-weight: normal;
	white-space: normal;
}
.col-label {
	font-weight: bold;
	font-size: 13px;
}
.col-address {
	font-weight: normal;
	font-size: 11px;
	color: #777;
	white-space: normal;
	max-width: 160px;
}
td.best {
	background: rgba(46, 125, 50, 0.15);
	font-weight: bold;
	color: #2e7d32;
	border-radius: 4px;
}
</style>
