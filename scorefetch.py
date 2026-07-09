import sqlite3, requests

key = "4ecf6f899a9e4587c6289422a3850d0fb9803dbc"

conn = sqlite3.connect("census.db")
cursor = conn.cursor()

url = "https://api.census.gov/data/2018/acs/acs5"
params = {'get': 'B25064_001E', 'for': 'county:*', 'key': key}
response = requests.get(url, params=params)
rows = response.json()

header = rows[0]
rent_i, state_i, county_i = header.index("B25064_001E"), header.index("state"), header.index("county")

records = []
for row in rows[1:]:
	rent = int(row[rent_i])
	if rent < 0: rent = None
	records.append((int(row[state_i]), int(row[county_i]), rent))

cursor.execute("DROP TABLE IF EXISTS Loading")
cursor.execute("CREATE TABLE Loading (state INTEGER, county INTEGER, rent2018 INTEGER)")
cursor.executemany("INSERT INTO Loading VALUES (?, ?, ?)", records)

try: cursor.execute("ALTER TABLE Costs ADD COLUMN rent2018 INTEGER")
except sqlite3.OperationalError: pass
cursor.execute("UPDATE Costs SET rent2018 = (SELECT Loading.rent2018 FROM Loading WHERE Loading.state = Costs.state AND Loading.county = Costs.county)")
cursor.execute("DROP TABLE Loading")
conn.commit()
conn.close()
print("rent2018 loaded.")
