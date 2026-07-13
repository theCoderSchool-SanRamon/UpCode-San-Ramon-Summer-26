import sqlite3, requests

with open(".census_key", "r") as f:
	key = f.read().strip()

conn = sqlite3.connect("census.db")
cursor = conn.cursor()

url = "https://api.census.gov/data/2023/acs/acs5"
params = {"get": "B01003_001E", "for": "county:*", "key": key}
response = requests.get(url, params=params)
rows = response.json()

header = rows[0]
pop_i, state_i, county_i = (
	header.index("B01003_001E"),
	header.index("state"),
	header.index("county"),
)

records = []
for row in rows[1:]:
	pop = int(row[pop_i])
	if pop < 0:
		pop = None
	records.append((int(row[state_i]), int(row[county_i]), pop))

cursor.execute("DROP TABLE IF EXISTS Loading")

cursor.execute("CREATE TABLE Loading (state INTEGER, county INTEGER, population INTEGER)")

cursor.executemany("INSERT INTO Loading VALUES (?, ?, ?)", records)

try:
	cursor.execute("ALTER TABLE Costs ADD COLUMN population INTEGER")
except sqlite3.OperationalError:
	pass

cursor.execute(
	"UPDATE Costs SET population = (SELECT Loading.population FROM Loading WHERE Loading.state = Costs.state AND Loading.county = Costs.county)"
)
cursor.execute("DROP TABLE Loading")

conn.commit()
conn.close()

print("population (B01003_001E, 2023 ACS5) loaded.")
