from fastapi import HTTPException

import json
import os
import re
from pathlib import Path
from threading import Lock

import requests
from dotenv import load_dotenv

load_dotenv()


def normalize_address(address: str) -> str:
	return re.sub(r"\s+", " ", address.strip().lower())


class RentCastRequester:
	def __init__(self):
		self.key = os.environ.get("RENTCAST_API_KEY")
		if not self.key:
			print("RentCast API key not found. Please provide RENTCAST_API_KEY in .env.")
		self.url = "https://api.rentcast.io/v1"

	def _get(self, path: str, address: str):
		if not self.key:
			return None
		try:
			response = requests.get(
				f"{self.url}{path}",
				params={"address": address},
				headers={"X-Api-Key": self.key},
				timeout=10,
			)
			if response.status_code != 200:
				print(f"RentCast {path} failed for '{address}': {response.status_code} {response.text[:300]}")
				return None
			return response.json()
		except (requests.RequestException, ValueError) as e:
			print(f"RentCast {path} errored for '{address}': {e}")
			return None

	def fetch(self, address: str) -> dict:
		properties = self._get("/properties", address)
		value = self._get("/avm/value", address)
		rent = self._get("/avm/rent/long-term", address)

		record = properties[0] if isinstance(properties, list) and properties else {}

		tax_annual = None
		tax_history = record.get("propertyTaxes")
		if tax_history:
			latest_year = max(tax_history, key=lambda y: int(y))
			tax_annual = tax_history[latest_year].get("total")

		return {
			"address": record.get("formattedAddress") or address,
			"beds": record.get("bedrooms"),
			"baths": record.get("bathrooms"),
			"sqft": record.get("squareFootage"),
			"yearBuilt": record.get("yearBuilt"),
			"county": record.get("county"),
			"state": record.get("state"),
			"latitude": record.get("latitude"),
			"longitude": record.get("longitude"),
			"propertyTaxAnnual": tax_annual,
			"priceEstimate": value.get("price") if value else None,
			"rentEstimate": rent.get("rent") if rent else None,
		}

def _has_property_data(data: dict) -> bool:
	if not data:
		return False
	fields = ("beds", "baths", "sqft", "priceEstimate", "rentEstimate")
	return any(data.get(f) is not None for f in fields)


def get_property(address: str) -> dict:
	address = (address or "").strip()
	if not address:
		raise HTTPException(status_code=422, detail="address must be provided.")

	key = normalize_address(address)
	data = RentCastRequester().fetch(address)

	if _has_property_data(data):
		return data
