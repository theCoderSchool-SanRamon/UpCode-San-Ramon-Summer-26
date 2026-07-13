import requests

# place = "53980"
# state = "06"

cache = {}

class APIRequester():
	def __init__(self, url: str):
		self.url = url
	def send_query(self, params: dict):
		return requests.get(self.url, params=params)


class CensusRequester():
	def __init__(self):
		try:
			with open(".census_key", "r") as f:
				key = f.read()
		except FileNotFoundError:
			input("Census API Key not found. Please provide at .census_key.")



def query_place(place, state: str, get):
	url = "https://api.census.gov/data/2024/acs/acs5"
	params = {
		"get": get,  # "NAME,B01001_001E"
		"for": f'place:{place.rjust(5,"0")}',
		"in": f'state:{state.rjust(2,"0")}',
		"key": key,
	}
	if (place, state, get) in cache:
		return cache[(place, state, get)]
	else:
		response = requests.get(url, params=params)
		data = response.json()
		cache[(place, state, get)] = data
		return data


def query_county(county, state: str, get):
	url = "https://api.census.gov/data/2024/acs/acs5"
	params = {
		"get": get,  # "NAME,B01001_001E"
		"for": f'county:{county.rjust(3,"0")}',
		"in": f'state:{state.rjust(2,"0")}',
		"key": key,
	}
	if (county, state, get) in cache:
		return cache[(county, state, get)]
	else:
		response = requests.get(url, params=params)
		data = response.json()
		cache[(county, state, get)] = data
		return data
