<script setup lang="ts">
import ToolDropdown from './ToolDropdown.vue';

</script>

<template>
	<ToolDropdown :icon-closed="'/greyicon.png'" :icon-open="'/favicon.ico'" style="image-rendering: pixelated; image-rendering: crisp-edges;">
		<div id="about-wrapper">
			<h3>About RealDeal</h3>
			<p>
				RealDeal is an app designed to help you find the best areas to invest.<br>
				Our heatmap shows the areas with the best price-to-rent ratios in green.
			</p>
		</div>
	</ToolDropdown>
</template>
<style scoped>
#about-wrapper {
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
#about-wrapper h3 {
	margin-bottom: 4px;
}
</style>