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
		<Transition><img :src="iconClosed" class="img-icon" v-if="!uiEnabled"></img></Transition>
		<Transition><img :src="iconOpen" class="img-icon" v-if="uiEnabled"></img></Transition>
	</button>

	<Transition name="slot">

	<div v-if="uiEnabled" class="wrap">
		<Transition name="slot">
			<slot v-if="uiEnabled"></slot>
		</Transition>
	</div>

	</Transition>
</div>

</template>

<style scoped>
.v-enter-active, .v-leave-active {
	transition: opacity 0.25s ease;
}
.v-enter-from, .v-leave-to {
	opacity: 0;
}
.wrap {
	margin-top: 40px;
	
	max-width: 100%;

	position: absolute;
}
.slot-enter-active {
	transition: 
	opacity 0.4s ease,
	max-width 1.9s ease,
	transform 0.5s cubic-bezier(0.16, 1, 0.5, 1)
	;
}
.slot-leave-active {
	transition: 
	opacity 0.4s ease,
	max-width 1s ease,
	transform 2s cubic-bezier(0.16, 1, 0.5, 1)
	;
}
.slot-enter-from, .slot-leave-to {
	transform: scale(0.9) translateY(-200%);
	opacity: 0;
	
}

.img-icon {
	width: 20px;
	height: 20px;
	object-fit: contain;
	position: absolute;
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
