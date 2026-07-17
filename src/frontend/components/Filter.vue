<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import ToolDropdown from './ToolDropdown.vue'
</script>

<template>
<ToolDropdown>
	<div class="filter-body">
	</div>
</ToolDropdown>
</template>

<style scoped>
.filter-body {
	pointer-events: auto;
	margin: 16px;
	padding: 16px;
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
	border-radius: 8px;
	overflow-y: auto;
	font: 13px Arial, sans-serif;
	border: var(--overlay-border);
	outline: none;
}
</style>
