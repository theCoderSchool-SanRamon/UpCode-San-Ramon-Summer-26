import requests

# place = "53980"
# state = "06"

cache = {}

class APIRequester():
	def __init__(self, url: str):
		self.url = url
	def send_query(self, params: dict):
		return requests.get(self.url, params=params)


class CensusRequester(APIRequester):
	def __init__(self):
		try:
			with open(".census_key", "r") as f:
				self.key = f.read()
			super().__init__(self, "https://api.census.gov/data/2024/acs/acs5")
		except FileNotFoundError:
			print("Census API Key not found. Please provide at .census_key.")
	def send_query(self, params: dict):
		if "place" in params: params["for"] = params.pop("place").rjust(5,"0")
		if "county" in params: params["for"] = params.pop("county").rjust(3,"0")
		if "state" in params: params["in"] = params.pop("state").rjust(2,"0")
		params["key"] = self.key
		return super().send_query(self, params)