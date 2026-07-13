import sqlite3, json, math

DATA_PATH = "src/assets/countydata.json"

FACTORS = {
	"ratio": {"weight": 0.30, "invert": True},
	"apprec": {"weight": 0.25, "invert": False},
	"rentGrowth": {"weight": 0.15, "invert": False},
	"tax": {"weight": 0.15, "invert": True},
	"vac": {"weight": 0.15, "invert": True},
}


def valid(x):
	"""ACS fields encode missing data as null or a negative sentinel (e.g. -666666666)."""
	return x is not None and x >= 0


def percentile(sorted_vals, p):
	k = (len(sorted_vals) - 1) * p
	f, c = math.floor(k), math.ceil(k)
	if f == c:
		return sorted_vals[int(k)]
	return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


conn = sqlite3.connect("census.db")
cursor = conn.cursor()
cursor.execute("""
	SELECT countyname, statename, houseprice, rent, rent2018, propertytax,
		vacantforrent, rentedunoccupied, renteroccupied, population, populationchange
	FROM Costs
""")
rows = cursor.fetchall()
conn.close()

counties = {}
for (
	countyname,
	statename,
	houseprice,
	rent,
	rent2018,
	propertytax,
	vacantforrent,
	rentedunoccupied,
	renteroccupied,
	population,
	populationchange,
) in rows:
	key = f"{countyname}_{statename}"

	ratio = (
		houseprice / (rent * 12)
		if valid(houseprice) and valid(rent) and rent > 0
		else None
	)
	apprec = (
		populationchange / population
		if population and population > 0 and populationchange is not None
		else None
	)
	rentGrowth = (
		(rent - rent2018) / rent2018
		if valid(rent) and valid(rent2018) and rent2018 > 0
		else None
	)
	tax = (
		propertytax / houseprice
		if valid(propertytax) and valid(houseprice) and houseprice > 0
		else None
	)
	vacDenom = (renteroccupied or 0) + (vacantforrent or 0) + (rentedunoccupied or 0)
	vac = (
		vacantforrent / vacDenom
		if valid(vacantforrent)
		and valid(rentedunoccupied)
		and valid(renteroccupied)
		and vacDenom > 0
		else None
	)
	
	counties[key] = {
		"population": population,
		"ratio": ratio,
		"apprec": apprec,
		"rentGrowth": rentGrowth,
		"tax": tax,
		"vac": vac,
	}

# Per-factor clamp range: 5th/95th percentile across counties with a non-null value.
ranges = {}
for name in FACTORS:
	vals = sorted(c[name] for c in counties.values() if c[name] is not None)
	if not vals:
		continue
	p5, p95 = percentile(vals, 0.05), percentile(vals, 0.95)
	clamped = [min(max(v, p5), p95) for v in vals]
	ranges[name] = {"p5": p5, "p95": p95, "min": min(clamped), "max": max(clamped)}

for key, factors in counties.items():
	weighted_sum, weight_present = 0.0, 0.0
	for name, cfg in FACTORS.items():
		raw = factors[name]
		if raw is None or name not in ranges:
			continue
		r = ranges[name]
		v = min(max(raw, r["p5"]), r["p95"])
		if r["max"] == r["min"]:
			norm = 1.0
		else:
			norm = (
				(r["max"] - v) / (r["max"] - r["min"])
				if cfg["invert"]
				else (v - r["min"]) / (r["max"] - r["min"])
			)
		norm = min(max(norm, 0.0), 1.0)
		weighted_sum += cfg["weight"] * norm
		weight_present += cfg["weight"]

	if weight_present > 0:
		factors["score"] = round(100 * weighted_sum / weight_present, 1)
		factors["partialData"] = (
			weight_present < sum(f["weight"] for f in FACTORS.values()) - 1e-9
		)
	else:
		factors["score"] = None
		factors["partialData"] = True

with open(DATA_PATH) as file:
	countyProperties = json.load(file)

for key, entry in countyProperties.items():
	entry.update(counties.get(key, {"score": None, "partialData": True}))

with open(DATA_PATH, "w") as file:
	json.dump(countyProperties, file)

print(
	f"Scored {sum(1 for c in counties.values() if c.get('score') is not None)} of {len(countyProperties)} counties."
)
