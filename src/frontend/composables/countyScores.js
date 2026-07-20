import { reactive, ref, computed, watch } from 'vue'

export const FACTORS = {
	ratio: { weight: 0.30, invert: true },
	apprec: { weight: 0.25, invert: false },
	rentGrowth: { weight: 0.15, invert: false },
	tax: { weight: 0.15, invert: true },
	vac: { weight: 0.15, invert: true },
}
export const DEFAULT_WEIGHTS = Object.fromEntries(
	Object.entries(FACTORS).map(([k, v]) => [k, v.weight])
)
const WEIGHT_SUM_TOLERANCE = 0.01

const rawCountyData = ref(null)
const loading = ref(false)
const loaded = ref(false)
const weights = reactive({ ...DEFAULT_WEIGHTS })
const countyScoresInternal = ref({})
const populationFilter = ref(0)

function percentile(sortedVals, p) {
	const k = (sortedVals.length - 1) * p
	const f = Math.floor(k), c = Math.ceil(k)
	if (f === c) return sortedVals[k]
	return sortedVals[f] * (c - k) + sortedVals[c] * (k - f)
}

const ranges = computed(() => {
	if (!rawCountyData.value) return null
	const out = {}
	for (const name of Object.keys(FACTORS)) {
		const vals = Object.values(rawCountyData.value)
			.map(c => c[name])
			.filter(v => v != null)
			.sort((a, b) => a - b)
		if (!vals.length) continue
		const p5 = percentile(vals, 0.05), p95 = percentile(vals, 0.95)
		const clamped = vals.map(v => Math.min(Math.max(v, p5), p95))
		out[name] = { p5, p95, min: Math.min(...clamped), max: Math.max(...clamped) }
	}
	return out
})

const normCache = computed(() => {
	if (!rawCountyData.value || !ranges.value) return null
	const cache = {}
	for (const [key, county] of Object.entries(rawCountyData.value)) {
		const norms = {}
		for (const [name, cfg] of Object.entries(FACTORS)) {
			const raw = county[name]
			const r = ranges.value[name]
			if (raw == null || !r) continue
			const v = Math.min(Math.max(raw, r.p5), r.p95)
			const norm = r.max === r.min
				? 1.0
				: cfg.invert ? (r.max - v) / (r.max - r.min) : (v - r.min) / (r.max - r.min)
			norms[name] = Math.min(Math.max(norm, 0), 1)
		}
		cache[key] = norms
	}
	return cache
})

const weightsSum = computed(() =>
	Object.values(weights).reduce((a, b) => a + (typeof b === 'number' && !Number.isNaN(b) ? b : 0), 0)
)
const weightsValid = computed(() =>
	Object.values(weights).every(w => typeof w === 'number' && !Number.isNaN(w) && w >= 0 && w <= 1) &&
	Math.abs(weightsSum.value - 1) < WEIGHT_SUM_TOLERANCE
)

function computeScore(norms) {
	let weightedSum = 0, weightPresent = 0
	for (const name of Object.keys(FACTORS)) {
		const norm = norms[name]
		if (norm == null) continue
		weightedSum += weights[name] * norm
		weightPresent += weights[name]
	}
	if (weightPresent <= 0) return { score: null, partialData: true }
	return {
		score: Math.round((100 * weightedSum / weightPresent) * 10) / 10,
		partialData: weightPresent < weightsSum.value - 1e-9,
	}
}

watch([normCache, weights], () => {
	if (!normCache.value || !weightsValid.value) return
	const out = {}
	for (const [key, norms] of Object.entries(normCache.value)) out[key] = computeScore(norms)
	countyScoresInternal.value = out
}, { immediate: true, deep: true })

export function useCountyScores() {
	async function ensureLoaded() {
		if (loaded.value || loading.value) return
		loading.value = true
		try {
			const res = await fetch('/countydata.json')
			rawCountyData.value = await res.json()
			loaded.value = true
		} finally {
			loading.value = false
		}
	}

	function resetWeights() {
		Object.assign(weights, DEFAULT_WEIGHTS)
	}

	function keyFor(name, state) {
		return `${name}_${state}`
	}

	return {
		weights,
		weightsSum,
		weightsValid,
		rawCountyData,
		loaded,
		loading,
		countyScores: computed(() => countyScoresInternal.value),
		ensureLoaded,
		resetWeights,
		keyFor,
		FACTORS,
		DEFAULT_WEIGHTS,
		populationFilter,
	}
}
