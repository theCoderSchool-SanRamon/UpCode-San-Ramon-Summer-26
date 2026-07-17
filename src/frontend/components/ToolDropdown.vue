<script setup>
import { computed, ref, watch, nextTick } from 'vue'

const props = defineProps({
	iconClosed: {type: String, default: ""},
	iconOpen: {type: String, default: ""},
})

const uiEnabled = ref(false);

</script>

<template>

<div id="toggle-wrapper">
	
<button id="toggle-button" @mousedown.prevent="uiEnabled = !uiEnabled">
</button>

<slot v-if="uiEnabled"></slot>

</div>

</template>

<style scoped>

.v-enter-active, .v-leave-active {
	transition: opacity 0.5s ease;
}
.v-enter-from, .v-leave-to {
	opacity: 0;
}

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
	display: flex;
	flex-direction: column;
	gap: 6px;
}
</style>
