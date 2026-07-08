import requests

url = "https://api.datausa.io/tesseract/data.jsonrecords"

params = {
    # 1. Use the dataset cube that actually supports the Place dimension
    "cube": "acs_ygpsar_poverty_by_gender_age_race_5",
    "drilldowns": "Place,Year",
    "measures": "Poverty Population",
    # 2. Poverty Status '0' pulls the baseline population count
    "include": "Place:16000US0653980;Poverty Status:0",
    "latest": "true" 
}

response = requests.get(url, params=params)
data = response.json()
print(data)
