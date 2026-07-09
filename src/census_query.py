with open(".census_key","r") as f: key=f.read()
import requests

#place = "53980"
#state = "06"

cache={}

def query(place,state,get):
	url = "https://api.census.gov/data/2024/acs/acs5"

	params = {
	'get':get,#'NAME,B01001_001E',
	'for':f'place:{place}',
	'in':f'state:{state}',
	'key':key,
	}
	if (place,state,get) in cache: 
		return cache[(place,state,get)]
	else:
		response = requests.get(url, params=params)
		data = response.json()
		cache[(place,state,get)]=data
		return data
