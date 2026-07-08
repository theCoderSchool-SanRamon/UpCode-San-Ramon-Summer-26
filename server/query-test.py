with open(".census_key","r") as f: key=f.read()
import requests

place = "53980"
state = "06"

url = "https://api.census.gov/data/2024/acs/acs5"

params = {
'get':'NAME,B01001_001E',
'for':f'place:{place}',
'in':f'state:{state}',
'key':key
}
response = requests.get(url, params=params)
data = response.json()
print(data)
