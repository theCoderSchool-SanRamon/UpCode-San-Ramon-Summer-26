<script setup>
import { nextTick, ref, watch } from 'vue'
import { useChat } from '../composables/chat.js'
import { renderMarkdown } from '../composables/markdown.js'

const { messages, isExpanded, sending, limited, toggleExpanded, sendMessage } = useChat()

const draft = ref('')
const messagesEl = ref(null)

function scrollToBottom() {
	nextTick(() => {
		if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
	})
}

watch(messages, scrollToBottom, { deep: true })
watch(isExpanded, (open) => { if (open) scrollToBottom() })

function submit() {
	const text = draft.value
	draft.value = ''
	sendMessage(text)
	scrollToBottom()
}
</script>

<template>

<div id="chat-widget">
	<div class="chat-panel" v-if="isExpanded">
		<div class="messages" ref="messagesEl">
			<div class="empty-hint" v-if="!messages.length">
				Ask me about cap rate, DSCR, or whatever county or property you're looking at.
			</div>
			<div
				v-for="(m, i) in messages"
				:key="i"
				class="msg"
				:class="m.role === 'user' ? 'user' : 'model'"
			>
				<span v-if="m.role === 'user'">{{ m.text }}</span>
				<div v-else class="markdown" v-html="renderMarkdown(m.text)"></div>
			</div>
			<div class="msg model typing" v-if="sending">Thinking…</div>
		</div>
		<form class="input-row" @submit.prevent="submit">
			<input
				type="text"
				v-model="draft"
				placeholder="Ask RealDeal…"
				:disabled="limited"
			/>
			<button type="submit" :disabled="sending || limited || !draft.trim()">Send</button>
		</form>
	</div>

	<button type="button" class="chat-header" @click="toggleExpanded">
		<span>Ask RealDeal</span>
		<span class="chevron">{{ isExpanded ? '▾' : '▴' }}</span>
	</button>
</div>

</template>

<style scoped>
#chat-widget {
	position: fixed;
	right: 16px;
	bottom: 16px;
	z-index: 100;
	display: flex;
	flex-direction: column;
	align-items: stretch;
	width: 400px;
	pointer-events: auto;
	font: 13px Arial, sans-serif;
}
.chat-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	border: var(--overlay-border);
	border-radius: 16px;
	padding: 10px 14px;
	font: 13px Arial, sans-serif;
	font-weight: bold;
	color: #333;
	cursor: pointer;
	outline: none;
}
.chat-header:hover {
	border-color: #666;
}
.chevron {
	color: #777;
	font-size: 11px;
}
.chat-panel {
	display: flex;
	flex-direction: column;
	margin-bottom: 8px;
	background: var(--overlay-background);
	backdrop-filter: var(--overlay-blur);
	border: var(--overlay-border);
	border-radius: 16px;
	overflow: hidden;
}
.messages {
	overflow-y: auto;
	scrollbar-width: none;
	padding: 14px;
	display: flex;
	flex-direction: column;
	gap: 10px;
	height: 460px;
}
.empty-hint {
	font: 12px Arial, sans-serif;
	color: #777;
	font-style: italic;
}
.msg {
	max-width: 90%;
	padding: 8px 12px;
	border-radius: 10px;
	font-size: 13px;
	line-height: 1.45;
	white-space: pre-wrap;
	word-break: break-word;
}
.msg.user {
	align-self: flex-end;
	background: #333;
	color: white;
}
.msg.model {
	align-self: flex-start;
	background: rgba(255, 255, 255, 0.85);
	color: #333;
	border: 1px solid #ddd;
}
.msg.typing {
	color: #999;
	font-style: italic;
}
.markdown :deep(p) {
	margin: 0 0 8px;
}
.markdown :deep(p:last-child) {
	margin-bottom: 0;
}
.markdown :deep(ul) {
	margin: 0 0 8px 18px;
}
.markdown :deep(ul:last-child) {
	margin-bottom: 0;
}
.markdown :deep(li) {
	margin-bottom: 3px;
}
.markdown :deep(code) {
	background: rgba(0, 0, 0, 0.08);
	padding: 1px 4px;
	border-radius: 3px;
	font-family: monospace;
	font-size: 12px;
}
.input-row {
	display: flex;
	gap: 6px;
	padding: 10px;
	border-top: var(--overlay-border);
}
.input-row input {
	flex: 1 1 auto;
	font: 12px Arial, sans-serif;
	border: 1px solid #ccc;
	border-radius: 6px;
	padding: 6px 8px;
	outline: none;
	background: white;
	min-width: 0;
}
.input-row input:focus {
	border-color: #666;
}
.input-row button {
	font: 12px Arial, sans-serif;
	font-weight: bold;
	padding: 6px 12px;
	border: 1px solid #ccc;
	border-radius: 6px;
	background: white;
	cursor: pointer;
}
.input-row button:hover:not(:disabled) {
	border-color: #666;
}
.input-row button:disabled {
	color: #999;
	cursor: default;
}
</style>
