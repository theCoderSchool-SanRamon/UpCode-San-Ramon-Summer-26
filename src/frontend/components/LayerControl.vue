<script setup>
import { ref, nextTick, watch } from 'vue';
import ToolDropdown from './ToolDropdown.vue'

const layerControlActive = ref(false)
const countyVisible = ref(true)
const cityVisible = ref(true)
const countyActive = ref(true)
const cityActive = ref(true)

const emit = defineEmits(["changed"])

watch(countyVisible, () => {emit("changed", {type: "visibility", layer: "county", value: countyVisible.value})})
watch(cityVisible, () => {emit("changed", {type: "visibility", layer: "city", value: cityVisible.value})})
watch(countyActive, () => {emit("changed", {type: "interactability", layer: "county", value: countyActive.value})})
watch(cityActive, () => {emit("changed", {type: "interactability", layer: "city", value: cityActive.value})})

</script>
<template>
	<ToolDropdown :icon-closed="'/openlayers.svg'" :icon-open="'/openlayers2.svg'">
		<div id="layer-control-wrapper">
			<h4>Show Layers:</h4>
			<div class="l-item">City<input type="checkbox" v-model="cityVisible" /> </div>
			<div class="l-item">County <input type="checkbox" v-model="countyVisible" /></div>
			<h4>Allow Hovering:</h4>
			<div class="l-item">City<input type="checkbox" v-model="cityActive" /> </div>
			<div class="l-item">County <input type="checkbox" v-model="countyActive" /></div>
		</div>
	</ToolDropdown>
</template>
<style scoped>
.l-item {
	width: 100%;
	display: inline-flex;
	justify-content: space-between;
}
#layer-control-button {
	pointer-events: auto;
}
#layer-control-wrapper {
	background: var(--overlay-background);
	margin: 16px;
	backdrop-filter: var(--overlay-blur);
	padding: 8px 10px;
	font: 14px Arial, sans-serif;
	border: var(--overlay-border);
	border-radius: 14px;
	outline: none;
	pointer-events: auto;
}
#layer-control-wrapper h4 {
	margin-bottom: 4px;
}
td {
	padding-left: 4px;
	padding-right: 4px;
}
</style>