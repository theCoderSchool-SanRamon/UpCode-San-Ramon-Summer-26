import { ref } from 'vue'
import { usePropertyAnalysis } from './propertyAnalysis.js'
import { useCountyScores } from './countyScores.js'

const MAX_HISTORY = 10
const TOP_COUNTIES_COUNT = 5

const messages = ref([])
const isExpanded = ref(false)
const sending = ref(false)
const error = ref(null)
const limited = ref(false)
const sessionId = crypto.randomUUID()

function topCounties(rawCountyData, countyScores, populationFilter) {
	if (!rawCountyData) return []
	const list = []
	for (const [key, raw] of Object.entries(rawCountyData)) {
		const info = countyScores[key]
		if (!info || info.score == null) continue
		if (populationFilter > 0 && !(raw.population >= populationFilter)) continue
		const splitAt = key.lastIndexOf('_')
		list.push({
			name: key.slice(0, splitAt),
			state: key.slice(splitAt + 1),
			score: info.score,
		})
	}
	list.sort((a, b) => b.score - a.score)
	return list.slice(0, TOP_COUNTIES_COUNT)
}

function buildContext() {
	const { currentProperty, computeMetrics, computePropertyScore, countyContext } = usePropertyAnalysis()
	const { rawCountyData, countyScores, weights, populationFilter } = useCountyScores()

	const property = currentProperty.value
	let propertyContext = null
	let county = null

	if (property) {
		const metrics = computeMetrics(property)
		propertyContext = {
			address: property.address,
			county: property.county,
			state: property.state,
			beds: property.beds,
			baths: property.baths,
			sqft: property.sqft,
			price: property.price,
			rent: property.rent,
			metrics,
			score: computePropertyScore(metrics),
		}
		const ctx = countyContext(property)
		if (ctx) {
			county = { name: property.county, state: property.state, score: ctx.score, factors: ctx.raw }
		}
	}

	return {
		property: propertyContext,
		county,
		leaderboard: {
			weights: { ...weights },
			populationFilter: populationFilter.value,
			topCounties: topCounties(rawCountyData.value, countyScores.value, populationFilter.value),
		},
	}
}

async function sendMessage(text) {
	const trimmed = (text || '').trim()
	if (!trimmed || sending.value || limited.value) return

	messages.value.push({ role: 'user', text: trimmed })
	sending.value = true
	error.value = null

	try {
		const history = messages.value.slice(-MAX_HISTORY)
		const res = await fetch('/api/chat', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ messages: history, context: buildContext(), sessionId }),
		})
		if (!res.ok) throw new Error(`Chat failed (${res.status})`)
		const data = await res.json()
		messages.value.push({ role: 'model', text: data.reply })
		if (data.limited) limited.value = true
	} catch (e) {
		error.value = e.message || 'Chat failed'
		messages.value.push({ role: 'model', text: "Sorry, I couldn't respond just now. Please try again." })
	} finally {
		sending.value = false
	}
}

function toggleExpanded() {
	isExpanded.value = !isExpanded.value
}

export function useChat() {
	return {
		messages,
		isExpanded,
		sending,
		error,
		limited,
		toggleExpanded,
		sendMessage,
	}
}
