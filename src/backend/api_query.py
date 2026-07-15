from fastapi import HTTPException

import requests

# place = "53980"
# state = "06"

cache = {}


class APIRequester:
	def __init__(self, url: str):
		self.url = url

	def send_query(self, **params: dict):
		return requests.get(self.url, params=params)


class CensusRequester(APIRequester):
	def __init__(self):
		try:
			with open(".census_key", "r") as f:
				self.key = f.read()
			super().__init__("https://api.census.gov/data/2024/acs/acs5")
		except FileNotFoundError:
			print("Census API Key not found. Please provide at .census_key.")

	def send_query(self, **params: dict):
		params = {k: v for k, v in params.items() if v != None}
		if "place" in params:
			params["for"] = "place:" + (params.pop("place").rjust(5, "0") if params["place"] != '*' else params.pop("place"))
		if "county" in params:
			params["for"] = "county:" + (params.pop("county").rjust(3, "0") if params["county"] != '*' else params.pop("county"))
		if len(params["for"]) > 11:
			raise HTTPException(status_code=422, detail="Invalid for argument.")
		if "state" in params:
			params["in"] = params.pop("state").rjust(2, "0")
			if len(params["in"]) != 2:
				raise HTTPException(status_code=422, detail="Invalid in argument.")
			params["in"] = "state:" + params["in"]
		params["key"] = self.key
		response = super().send_query(**params)
		output = response.json()
		output.pop(0)
		return {x[len(x) - 2] + x[len(x) - 1]: x[: len(x) - 2] for x in output}
