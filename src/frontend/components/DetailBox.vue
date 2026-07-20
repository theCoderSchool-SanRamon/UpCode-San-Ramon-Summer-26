<script setup>
import { ref } from 'vue';

const detailVisible = ref(false)
const detailBoxContainerRef = ref(null)

function activateDetail(feature, place) {
	detailVisible.value = true
	detailBoxContainerRef.value.focus()
}

function deactivate() {
	detailVisible.value = false
}

defineExpose({
	activateDetail
})
</script>

<template>
	<div id="detail-box-backing" v-show="detailVisible" @click.self="deactivate()">
		<div id="detail-box-container" ref="detailBoxContainerRef">
			
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