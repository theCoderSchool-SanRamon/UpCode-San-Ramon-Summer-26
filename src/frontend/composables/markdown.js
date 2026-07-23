function escapeHtml(text) {
	return text
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;')
}

function inlineFormat(text) {
	return text
		.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
		.replace(/(^|[^*])\*([^*\s][^*]*?)\*(?!\*)/g, '$1<em>$2</em>')
		.replace(/`([^`]+?)`/g, '<code>$1</code>')
}

export function renderMarkdown(raw) {
	const lines = escapeHtml(raw || '').replace(/\$\$?/g, '').split('\n')
	const blocks = []
	let listItems = []
	let paragraph = []

	function flushList() {
		if (!listItems.length) return
		blocks.push('<ul>' + listItems.map((item) => `<li>${inlineFormat(item)}</li>`).join('') + '</ul>')
		listItems = []
	}
	function flushParagraph() {
		if (!paragraph.length) return
		blocks.push('<p>' + inlineFormat(paragraph.join(' ')) + '</p>')
		paragraph = []
	}

	for (const line of lines) {
		const trimmed = line.trim()
		if (!trimmed) {
			flushParagraph()
			flushList()
			continue
		}
		const listMatch = trimmed.match(/^[-*]\s+(.*)/)
		if (listMatch) {
			flushParagraph()
			listItems.push(listMatch[1])
			continue
		}
		const headingMatch = trimmed.match(/^#{1,6}\s+(.*)/)
		if (headingMatch) {
			flushParagraph()
			flushList()
			blocks.push(`<p><strong>${inlineFormat(headingMatch[1])}</strong></p>`)
			continue
		}
		flushList()
		paragraph.push(trimmed)
	}
	flushParagraph()
	flushList()

	return blocks.join('')
}
