import sqlite3, pandas
from sys import argv

conn = sqlite3.connect("census.db")
cursor = conn.cursor()

if len(argv) <= 1: targetFile = input("Enter file to load: ").replace('\\', '/')
else: targetFile = argv[1].replace('\\', '/')
if targetFile.endswith("json"):
	print("Attempting to open Census-formatted JSON.")
	with open(targetFile) as file: dataframe = pandas.read_json(file, orient="records")
	columnname = dataframe.iloc[0][0]
	dataframe.columns = dataframe.iloc[0]
	dataframe = dataframe.drop(0).dropna().astype(int)
elif targetFile.endswith("csv"):
	print("Attempting to open formatted CSV.")
	with open(targetFile) as file: dataframe = pandas.read_csv(file)
	columnname = input("Target column name: ")
	if not columnname in dataframe.columns:
		print("Incorrect column name.")
else:
	print("File type not recognized.")
dataframe.to_sql("Loading", conn, index=False, dtype="INTEGER")

preferred = input("Preferred column name: ").lower()
if "county" in dataframe.columns:
	cursor.execute(f"ALTER TABLE Costs ADD COLUMN {preferred} INTEGER")
	cursor.execute(f"UPDATE Costs SET {preferred} = (SELECT Loading.{columnname} FROM Loading WHERE Loading.state = Costs.state AND Loading.county = Costs.county)")
	print("Inserted into Costs.")
elif "place" in dataframe.columns:
	cursor.execute(f"ALTER TABLE PlaceAttributes ADD COLUMN {preferred} INTEGER")
	cursor.execute(f"UPDATE PlaceAttributes SET {preferred} = (SELECT Loading.{columnname} FROM Loading WHERE Loading.state = PlaceAttributes.state AND Loading.place = PlaceAttributes.place)")
	print("Inserted into PlaceAttributes.")
else:
	print("Unable to recognize data type.")
cursor.execute("DROP TABLE Loading")
conn.commit()
conn.close()