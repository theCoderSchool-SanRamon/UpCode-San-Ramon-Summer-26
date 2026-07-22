<script setup>
import { Chart, RadarController, RadialLinearScale, PointElement, LineElement } from 'chart.js';
import { onMounted, ref } from 'vue';

Chart.register(RadarController, RadialLinearScale, PointElement, LineElement)

const detailVisible = ref(false)
const radarCanvas = ref(null)
const activeChart = ref(null)

const invlerp = (l, u, v) => (v - l) / (u - l)

const chartLoading = ref(true)

function activateDetail(feature, place) {
	if (!feature) {return}
	detailVisible.value = true
	buildChart(place ? fetch("/api/census?query=B25077_001E,B25058_001E,B01003_001E&place=" + feature.get("PLACEFP") + "&state=" + feature.get("STATEFP")) : fetch("/api/census?query=B25077_001E,B25058_001E,B01003_001E&county=" + feature.get("COUNTYFP") + "&state=" + feature.get("STATEFP")))
}

async function buildChart(data) {
	data = await data
	data = Object.values(await data.json())[0]
	data[0] = data[0] > 0 ? invlerp(0, 2000000, data[0]) : null
	data[1] = data[1] > 0 ? invlerp(0, 3000, data[1]) : null
	data[2] = Math.log(data[2] / 100) / Math.log(4000000 / 100)
	chartLoading.value = false
	activeChart.value = new Chart(radarCanvas.value, {
		type: "radar",
		data: {
			labels: ["Price", "Rent", "Population"],
			datasets: [{
				data: Object.values(data)
			}]
		},
		options: {
			scales: {
				r: {
					min: 0,
					max: 1,
					ticks: {
						display: false
					}
				}
			}
		}
	})
}

function deactivate() {
	detailVisible.value = false
	activeChart.value.destroy()
	chartLoading.value = true
}

onMounted(async () => {
	
})

defineExpose({
	activateDetail
})
</script>

<template>
	<Transition>
	<div id="detail-box-backing" v-show="detailVisible" @click.self="deactivate()">
		<Transition>
		<div id="detail-box-container">
			<img style="width: 25%; aspect-ratio: 1; object-fit: cover;" src="/loading-9.gif" v-if="chartLoading" />
			<canvas id="radar" ref="radarCanvas"></canvas>
		</div>
		</Transition>
	</div>
</Transition>
</template>

<style scoped>
.v-enter-active, .v-leave-active {
	transition: opacity 0.5s ease;
}
.v-enter-from, .v-leave-to {
	opacity: 0;
}
.v-enter-active #detail-box-container,
.v-leave-active #detail-box-container {
	transition: transform 0.4s cubic-bezier(0.16, 1, 0.5, 1);
}
.v-enter-from #detail-box-container {
	transform: scale(0.9) translateY(130%);
}
.v-leave-to #detail-box-container {
	transform: scale(0.9);
}
#detail-box-backing {
	pointer-events: auto;
	width: 100%;
	height: 100%;
	padding-top: 6.25%;
	background-color: #2f4f4f3f;
}
#detail-box-container {
	background-color: white;
	width: 50%;
	height: 75vh;
	z-index: 102;
	padding: 16px;
	margin-left: 25%;
	border-radius: 8px;
	pointer-events: auto;
	display: grid;
	place-items: center;
}
</style>