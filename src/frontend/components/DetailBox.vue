<script setup>
import { Chart, RadarController, RadialLinearScale, PointElement, LineElement } from 'chart.js';
import { ref } from 'vue';

Chart.register(RadarController, RadialLinearScale, PointElement, LineElement)

const detailVisible = ref(false)
const radarCanvas = ref(null)
const activeChart = ref(null)

function activateDetail(feature, place) {
	if (!feature) {return}
	detailVisible.value = true
	buildChart(place ? fetch("/api/census?query=B25077_001E,B25058_001E,B01003_001E&place=" + feature.get("PLACEFP") + "&state=" + feature.get("STATEFP")) : null) // fetch("/api/census?query=B25077_001E,B25058_001E,B01003_001E&county=")) // not possible with current data set
}

async function buildChart(data) {
	data = await data
	data = await data.json()
	console.log(Object.values(data))
	activeChart.value = new Chart(radarCanvas.value, {
		type: "radar",
		data: {
			labels: ["Price", "Rent", "Population"],
			datasets: [{
				data: Object.values(data)[0]
			}]
		}
	})
}

function deactivate() {
	detailVisible.value = false
	activeChart.value.destroy()
}

defineExpose({
	activateDetail
})
</script>

<template>
	<div id="detail-box-backing" v-show="detailVisible" @click.self="deactivate()">
		<div id="detail-box-container">
			<canvas id="radar" ref="radarCanvas"></canvas>
		</div>
	</div>
</template>

<style scoped>
#detail-box-backing {
	pointer-events: auto;
	width: 100%;
	height: 100%;
	padding-top: 6.25%;
	background-color: #2f4f4f3f;
}
#detail-box-container {
	background-color: azure;
	width: 75%;
	height: 75vh;
	z-index: 102;
	padding: 16px;
	margin-left: 12.5%;
	border-radius: 8px;
	pointer-events: auto;
}
</style>