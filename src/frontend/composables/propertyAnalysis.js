import { reactive, ref } from 'vue'
import { useCountyScores } from './countyScores.js'

export const DEFAULT_ASSUMPTIONS = {
	downPaymentPct: 25,
	mortgageRatePct: 7,
	termYears: 30,
	vacancyPct: 8,
	managementPct: 8,
	maintenancePct: 5,
	closingCostPct: 3,
}
export const DEFAULT_INSURANCE_ANNUAL = 1500
export const MAX_COMPARE = 4

const COUNTY_SUFFIX_RE = /\s+(county|parish|borough|census area|municipality|municipio|city and borough)$/i

const assumptions = reactive({ ...DEFAULT_ASSUMPTIONS })
const currentProperty = ref(null)
const compareList = ref([])
const loading = ref(false)
const error = ref(null)
const addressQuery = ref('')
let nextId = 1

function normalizeCountyName(name) {
	if (!name) return null
	return name.replace(COUNTY_SUFFIX_RE, '').trim()
}

function buildProperty(raw, address) {
	return reactive({
		id: nextId++,
		address: raw.address || address,
		beds: raw.beds ?? null,
		baths: raw.baths ?? null,
		sqft: raw.sqft ?? null,
		yearBuilt: raw.yearBuilt ?? null,
		county: raw.county ?? null,
		state: raw.state ?? null,
		latitude: raw.latitude ?? null,
		longitude: raw.longitude ?? null,
		priceEstimate: raw.priceEstimate ?? null,
		rentEstimate: raw.rentEstimate ?? null,
		price: raw.priceEstimate ?? null,
		rent: raw.rentEstimate ?? null,
		propertyTaxFromRentCast: raw.propertyTaxAnnual != null,
		propertyTaxAnnual: raw.propertyTaxAnnual ?? null,
		insuranceAnnual: DEFAULT_INSURANCE_ANNUAL,
	})
}

export function usePropertyAnalysis() {
	const { rawCountyData, countyScores, keyFor, ensureLoaded } = useCountyScores()

	function matchCountyKey(property) {
		if (!property?.county || !property?.state || !rawCountyData.value) return null
		const key = keyFor(normalizeCountyName(property.county), property.state)
		return rawCountyData.value[key] ? key : null
	}

	function countyContext(property) {
		const key = matchCountyKey(property)
		if (!key) return null
		return {
			key,
			raw: rawCountyData.value[key],
			score: countyScores.value[key]?.score ?? null,
			partialData: countyScores.value[key]?.partialData ?? false,
		}
	}

	async function fetchProperty(address) {
		loading.value = true
		error.value = null
		try {
			const [res] = await Promise.all([
				fetch(`/api/property?address=${encodeURIComponent(address)}`),
				ensureLoaded(),
			])
			if (!res.ok) throw new Error(`Lookup failed (${res.status})`)
			const raw = await res.json()
			const property = buildProperty(raw, address)

			if (property.propertyTaxAnnual == null) {
				const ctx = countyContext(property)
				const rate = ctx?.raw?.tax
				if (rate != null && property.price != null) {
					property.propertyTaxAnnual = Math.round(rate * property.price)
				}
			}

			currentProperty.value = property
			return property
		} catch (e) {
			error.value = e.message || 'Lookup failed'
			currentProperty.value = null
			throw e
		} finally {
			loading.value = false
		}
	}

	function addToCompare(property) {
		if (!property) return
		if (compareList.value.some(p => p.id === property.id)) return
		if (compareList.value.length >= MAX_COMPARE) return
		compareList.value.push(property)
	}

	function removeFromCompare(id) {
		compareList.value = compareList.value.filter(p => p.id !== id)
	}

	function clearCompare() {
		compareList.value = []
	}

	function resetAssumptions() {
		Object.assign(assumptions, DEFAULT_ASSUMPTIONS)
	}

	function computeMetrics(property) {
		if (!property) return null
		const price = Number(property.price)
		const rent = Number(property.rent)
		const hasPrice = property.price != null && !Number.isNaN(price) && price > 0
		const hasRent = property.rent != null && !Number.isNaN(rent) && rent > 0

		const annualRent = hasRent ? rent * 12 : null
		const grossYield = hasPrice && annualRent != null ? annualRent / price : null

		const propertyTax = Number(property.propertyTaxAnnual) || 0
		const insurance = Number(property.insuranceAnnual) || 0
		const vacancyCost = annualRent != null ? (assumptions.vacancyPct / 100) * annualRent : 0
		const managementCost = annualRent != null ? (assumptions.managementPct / 100) * annualRent : 0
		const maintenanceCost = annualRent != null ? (assumptions.maintenancePct / 100) * annualRent : 0

		const NOI = annualRent != null
			? annualRent - vacancyCost - managementCost - maintenanceCost - propertyTax - insurance
			: null
		const capRate = hasPrice && NOI != null ? NOI / price : null

		const loanAmount = hasPrice ? price * (1 - assumptions.downPaymentPct / 100) : null
		const monthlyRate = assumptions.mortgageRatePct / 100 / 12
		const numPayments = assumptions.termYears * 12
		let monthlyMortgage = null
		if (loanAmount != null) {
			monthlyMortgage = monthlyRate === 0
				? loanAmount / numPayments
				: loanAmount * monthlyRate / (1 - Math.pow(1 + monthlyRate, -numPayments))
		}

		const monthlyExpenses = (vacancyCost + managementCost + maintenanceCost + propertyTax + insurance) / 12
		const monthlyCashFlow = hasRent && monthlyMortgage != null
			? rent - monthlyExpenses - monthlyMortgage
			: null

		const closingCosts = hasPrice ? (assumptions.closingCostPct / 100) * price : 0
		const cashInvested = hasPrice ? price * (assumptions.downPaymentPct / 100) + closingCosts : null
		const annualCashFlow = monthlyCashFlow != null ? monthlyCashFlow * 12 : null
		const cashOnCash = cashInvested ? annualCashFlow / cashInvested : null

		const annualDebtService = monthlyMortgage != null ? monthlyMortgage * 12 : null
		const DSCR = NOI != null && annualDebtService ? NOI / annualDebtService : null

		return { grossYield, NOI, capRate, monthlyMortgage, monthlyCashFlow, cashOnCash, DSCR }
	}

	return {
		assumptions,
		currentProperty,
		compareList,
		loading,
		error,
		addressQuery,
		MAX_COMPARE,
		fetchProperty,
		addToCompare,
		removeFromCompare,
		clearCompare,
		resetAssumptions,
		computeMetrics,
		countyContext,
	}
}
