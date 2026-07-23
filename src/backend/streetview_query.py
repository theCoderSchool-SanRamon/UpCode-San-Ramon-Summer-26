from fastapi import HTTPException, Response

import json
import os
from pathlib import Path
from threading import Lock

import requests
from dotenv import load_dotenv

load_dotenv()

CACHE_PATH = Path(__file__).resolve().parent.parent.parent / "streetview_cache.json"
IMG_DIR = Path(__file__).resolve().parent.parent.parent / "streetview_imgs"
_cache_lock = Lock()


def _key(lat: float, lng: float) -> str:
	return f"{lat + 0.0:.6f},{lng + 0.0:.6f}"


def _load_cache() -> dict:
	if not CACHE_PATH.exists():
		return {}
	try:
		with open(CACHE_PATH, "r") as f:
			return json.load(f)
	except (json.JSONDecodeError, OSError):
		return {}


def _save_cache(cache: dict):
	with open(CACHE_PATH, "w") as f:
		json.dump(cache, f, indent=2)


class StreetViewRequester:
	def __init__(self):
		self.key = os.environ.get("GOOGLE_STREETVIEW_KEY")
		if not self.key:
			print("Google Street View API key not found. Please provide GOOGLE_STREETVIEW_KEY in .env.")
		self.url = "https://maps.googleapis.com/maps/api/streetview"

	def check_available(self, lat: float, lng: float) -> bool | None:
		"""True/False for a definitive result, None for a transient failure that shouldn't be cached."""
		if not self.key:
			return None
		try:
			response = requests.get(
				f"{self.url}/metadata",
				params={"location": f"{lat},{lng}", "key": self.key},
				timeout=10,
			)
			if response.status_code != 200:
				return None
			status = response.json().get("status")
			if status == "OK":
				return True
			if status in ("ZERO_RESULTS", "NOT_FOUND"):
				return False
			return None
		except (requests.RequestException, ValueError):
			return None

	def fetch_image_bytes(self, lat: float, lng: float, size: str) -> bytes | None:
		if not self.key:
			return None
		try:
			response = requests.get(
				self.url,
				params={"size": size, "location": f"{lat},{lng}", "key": self.key},
				timeout=10,
			)
			if response.status_code != 200:
				return None
			return response.content
		except requests.RequestException:
			return None


def _get_availability(lat: float, lng: float) -> bool | None:
	key = _key(lat, lng)
	with _cache_lock:
		cache = _load_cache()
		if key in cache:
			return cache[key]["available"]

		available = StreetViewRequester().check_available(lat, lng)
		if available is not None:
			cache[key] = {"available": available}
			_save_cache(cache)
		return available


ALLOWED_SIZES = {"400x300", "600x450"}
DEFAULT_SIZE = "400x300"


def get_streetview_meta(lat: float, lng: float) -> dict:
	if not _get_availability(lat, lng):
		return {"photoUrl": None}
	return {"photoUrl": f"/api/streetview/img?lat={lat}&lng={lng}"}


def get_streetview_image(lat: float, lng: float, size: str = DEFAULT_SIZE) -> Response:
	if size not in ALLOWED_SIZES:
		size = DEFAULT_SIZE

	if not _get_availability(lat, lng):
		raise HTTPException(status_code=404, detail="No Street View imagery available.")

	key = _key(lat, lng)
	img_path = IMG_DIR / f"{key.replace(',', '_')}_{size}.jpg"

	with _cache_lock:
		if not img_path.exists():
			img_bytes = StreetViewRequester().fetch_image_bytes(lat, lng, size)
			if img_bytes is None:
				raise HTTPException(status_code=502, detail="Street View image fetch failed.")
			IMG_DIR.mkdir(exist_ok=True)
			with open(img_path, "wb") as f:
				f.write(img_bytes)
			return Response(content=img_bytes, media_type="image/jpeg")

		with open(img_path, "rb") as f:
			return Response(content=f.read(), media_type="image/jpeg")
