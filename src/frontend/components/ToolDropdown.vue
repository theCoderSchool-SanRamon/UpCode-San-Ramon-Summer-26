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

<Transition name="slot">
<slot v-if="uiEnabled"></slot>
</Transition>

</div>

</template>

<style scoped>

.slot-enter-active {
	transition: 
	opacity 0.4s ease,
	width 0s ease,
	transform 0.5s cubic-bezier(0.16, 1, 0.5, 1)
	;
}
.slot-leave-active {
	transition: 
	opacity 0.1s ease,
	width 0s ease,
	transform 0.5s cubic-bezier(0.16, 1, 0.5, 1)
	;
}
.slot-enter-from, .slot-leave-to {
	transform: scale(0.9) translateY(-200%);
	opacity: 0;
	width: 0px;
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
