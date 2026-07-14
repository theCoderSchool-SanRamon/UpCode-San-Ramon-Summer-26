<script setup>
import { onMounted, ref } from 'vue'

const searchQuery = ref("");

</script>

<template>

<div id="search-wrapper">
	<input
	class="search-input"
	type="text"
	v-model="searchQuery"
	placeholder="Search county..."
	autocomplete="off"
	/>
</div>
</template>

<style scoped>
#search-wrapper {

}
.search-input {
	width: 25%;
	margin: 16px;
	background: var(--overlay-background);
	backdrop-filter: blur(5px);
	padding: 8px 10px;
	font: 14px Arial, sans-serif;
	border: 1px solid #ccc;
	border-radius: 14px;
	outline: none;
	pointer-events: auto;
}
.search-input:focus {
	border-color: #666;
}
</style>