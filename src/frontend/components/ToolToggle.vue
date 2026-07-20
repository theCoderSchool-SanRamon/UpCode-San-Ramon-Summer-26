<script setup>
import { computed, ref, watch, nextTick } from 'vue'

const props = defineProps({
	icon: {type: String, default: ""},
})



const enabled = ref(false);

const emit = defineEmits(["changed"])
watch(enabled, () => {emit("changed", {type: "toggle", value: enabled.value})})

</script>

<template>

<div id="toggle-wrapper">
	
<button id="toggle-button" @mousedown.prevent="enabled = !enabled">
	<img :src="icon" class="img-icon"></img>
</button>

</div>

</template>

<style scoped>
.img-icon {
	width: 20px;
	height: 20px;
	object-fit: contain;
}

#toggle-button {
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	border: var(--overlay-border);
	border-radius: 14px;
	width: 32px;
	height: 32px;
	padding: 8px 10px;
	outline: none;
	margin: 16px;
	pointer-events: auto;
	font: 24px Arial, sans-serif;
	text-align: center;
	justify-content: center;
	align-items: center;
	min-width: 16px;
	min-height: 16px;
	display: inline-flex;
	gap: 6px;
	cursor: pointer;
}
#toggle-wrapper {
	min-width: 16px;
	min-height: 16px;
	overflow: hidden;
	display: flex;
	flex-direction: column;
	gap: 6px;
}
</style>
