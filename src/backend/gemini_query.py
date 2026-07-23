from fastapi import HTTPException

import json
import os
from threading import Lock

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
MAX_HISTORY = 10
MAX_OUTPUT_TOKENS = 2048
RATE_LIMIT_PER_SESSION = 20
RATE_LIMIT_MESSAGE = (
	"You've reached the limit of 20 messages for this session. "
	"Refresh the page to start a new session."
)

SYSTEM_PROMPT = """You are the RealDeal Assistant, a real estate investing assistant built into an app called RealDeal.

ROLE
Explain real estate investing terms in plain English when asked: cap rate, DSCR, cash-on-cash return, NOI, gross yield, price-to-rent ratio, vacancy rate, and appreciation. Be concise and approachable.

APP KNOWLEDGE
RealDeal ranks every US county with a 0-100 investment score built from six weighted factors: price-to-rent ratio, appreciation, rent growth, property tax, vacancy, and population. Users can set custom weights for these factors (they must sum to 1.00) and filter counties by a minimum population. The deal analyzer takes a property address and returns cap rate, cash flow, cash-on-cash return, DSCR, and a 0-100 property score, all computed from editable assumptions (down payment, mortgage rate, term, vacancy, management, maintenance, closing costs). Users can compare up to 4 properties side by side.

LIVE CONTEXT
Each message may include a JSON "context" block describing the county and/or property the user is currently viewing on screen (name, score, factor values, and any computed property metrics). Use it to answer questions about what's currently displayed. If the user asks about a number that isn't present in the provided context, say you don't have that figure rather than guessing or making one up.

GUARDRAILS
Stay strictly on topic: real estate investing concepts and how to use the RealDeal app. Politely decline requests unrelated to these topics. Never give financial advice or tell the user whether to buy or not buy a property — explain what the numbers mean and let the user draw their own conclusions.

FORMATTING
You're replying inside a narrow chat widget, not a document. Keep answers short. Use only plain markdown: **bold** for emphasis and "- " bullet lists where they genuinely help. Do not use headings (#, ##, ###), tables, code blocks, or LaTeX/math notation ($$...$$) — write any formula as plain text, e.g. "Cap Rate = NOI ÷ Purchase Price"."""

_session_lock = Lock()
_session_counts = {}


class GeminiRequester:
	def __init__(self):
		self.key = os.environ.get("GEMINI_API_KEY")
		if not self.key:
			print("Gemini API key not found. Please provide GEMINI_API_KEY in .env.")

	def generate(self, contents: list, system_instruction: str) -> str | None:
		if not self.key:
			return None
		try:
			response = requests.post(
				GEMINI_URL,
				params={"key": self.key},
				json={
					"contents": contents,
					"systemInstruction": {"parts": [{"text": system_instruction}]},
					"generationConfig": {"maxOutputTokens": MAX_OUTPUT_TOKENS},
				},
				timeout=20,
			)
			if response.status_code != 200:
				print(f"Gemini generateContent failed: {response.status_code} {response.text[:300]}")
				return None
			data = response.json()
			candidates = data.get("candidates") or []
			if not candidates:
				return None
			parts = candidates[0].get("content", {}).get("parts", [])
			text = "".join(p.get("text", "") for p in parts).strip()
			return text or None
		except (requests.RequestException, ValueError) as e:
			print(f"Gemini generateContent errored: {e}")
			return None


def _build_contents(messages: list) -> list:
	contents = []
	for m in messages[-MAX_HISTORY:]:
		role = "model" if m.get("role") == "model" else "user"
		text = m.get("text")
		if not text:
			continue
		contents.append({"role": role, "parts": [{"text": text}]})
	return contents


def _check_and_increment(session_id: str) -> bool:
	with _session_lock:
		count = _session_counts.get(session_id, 0)
		if count >= RATE_LIMIT_PER_SESSION:
			return False
		_session_counts[session_id] = count + 1
		return True


def get_chat_reply(payload: dict) -> dict:
	session_id = (payload.get("sessionId") or "").strip()
	if not session_id:
		raise HTTPException(status_code=422, detail="sessionId must be provided.")

	messages = payload.get("messages") or []
	context = payload.get("context") or {}

	if not _check_and_increment(session_id):
		return {"reply": RATE_LIMIT_MESSAGE, "limited": True}

	contents = _build_contents(messages)
	if not contents:
		raise HTTPException(status_code=422, detail="messages must contain at least one entry.")

	system_instruction = SYSTEM_PROMPT + "\n\nCurrent screen context (JSON):\n" + json.dumps(context)
	reply = GeminiRequester().generate(contents, system_instruction)
	if reply is None:
		raise HTTPException(status_code=502, detail="Chat service is unavailable right now.")

	return {"reply": reply, "limited": False}
