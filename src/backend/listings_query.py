from fastapi import HTTPException

import json
import os
from pathlib import Path
from threading import Lock

import requests
from dotenv import load_dotenv

load_dotenv()

BUCKET_STEP = 0.05

def bucket_key(lat: float, lon: float, radius: float) -> str:
	blat = round(lat / BUCKET_STEP) * BUCKET_STEP
	blon = round(lon / BUCKET_STEP) * BUCKET_STEP
	return f"{blat:.2f},{blon:.2f},{round(radius)}"


class RentCastListingsRequester:
	def __init__(self):
		self.key = os.environ.get("RENTCAST_API_KEY")
		if not self.key:
			print("RentCast API key not found. Please provide RENTCAST_API_KEY in .env.")
		self.url = "https://api.rentcast.io/v1/listings/sale"

	def fetch(self, lat: float, lon: float, radius: float, limit: int = 60) -> list:
		if not self.key:
			return []
		try:
			response = requests.get(
				self.url,
				params={
					"latitude": lat,
					"longitude": lon,
					"radius": radius,
					"status": "Active",
					"limit": limit,
				},
				headers={"X-Api-Key": self.key},
				timeout=10,
			)
			if response.status_code != 200:
				return []
			data = response.json()
			return data if isinstance(data, list) else []
		except (requests.RequestException, ValueError):
			return []

def get_listings(lat: float, lon: float, radius: float) -> list:
	if lat is None or lon is None:
		raise HTTPException(status_code=422, detail="lat and lon must be provided.")
	radius = max(1.0, min(radius or 3.0, 10.0))

	key = bucket_key(lat, lon, radius)
	raw = RentCastListingsRequester().fetch(lat, lon, radius)
	listings = [
		{
			"address": r.get("formattedAddress"),
			"price": r.get("price"),
			"latitude": r.get("latitude"),
			"longitude": r.get("longitude"),
			"beds": r.get("bedrooms"),
			"baths": r.get("bathrooms"),
			"sqft": r.get("squareFootage"),
		}
		for r in raw
		if r.get("latitude") is not None and r.get("longitude") is not None and r.get("price")
	]
	return listings
