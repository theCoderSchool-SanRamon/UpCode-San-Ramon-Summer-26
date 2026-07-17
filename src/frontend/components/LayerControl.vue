<script setup>
import { ref, nextTick, watch } from 'vue';

const layerControlActive = ref(false)
const countyVisible = ref(true)
const cityVisible = ref(true)
const countyActive = ref(true)
const cityActive = ref(false)

const emit = defineEmits(["changed"])

watch(countyVisible, () => {emit("changed", {type: "visibility", layer: "county", value: countyVisible.value})})
watch(cityVisible, () => {emit("changed", {type: "visibility", layer: "city", value: cityVisible.value})})
watch(countyActive, () => {emit("changed", {type: "interactability", layer: "county", value: countyActive.value})})
watch(cityActive, () => {emit("changed", {type: "interactability", layer: "city", value: cityActive.value})})

async function onLayerControlButton() {
	layerControlActive.value=!layerControlActive.value
	/*if (layerControlActive.value) {
		await nextTick()
		searchInputEntry.value.focus()
	}*/
}
</script>
<template>
	<div id="layer-control-container">
		<button id="layer-control-button" v-if="!layerControlActive" @click="onLayerControlButton()">
			🗃️
		</button>
		<div id="layer-control-wrapper" v-if="layerControlActive">
			<tr>
				<td>
					<input type="checkbox" v-model="countyVisible" checked>
				</td>
				<td>
					<input type="radio" name="active-layer" v-model="countyActive" checked>
				</td>
				<td>
					<p>
						County
					</p>
				</td>
			</tr>
			<tr>
				<td>
					<input type="checkbox" v-model="cityVisible" checked>
				</td>
				<td>
					<input type="radio" name="active-layer" v-model="cityActive">
				</td>
				<td>
					<p>
						City
					</p>
				</td>
			</tr>
		</div>
	</div>
</template>
<style scoped>
#layer-control-button {
	pointer-events: auto;
}
#layer-control-wrapper {
	width: 256px;
	margin: 16px;
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	padding: 8px 10px;
	font: 14px Arial, sans-serif;
	border: var(--overlay-border);
	border-radius: 14px;
	outline: none;
	pointer-events: auto;
}
td {
	padding-left: 4px;
	padding-right: 4px;
}
</style>