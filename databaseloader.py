import sqlite3, pandas
from sys import argv

conn = sqlite3.connect("census.db")
cursor = conn.cursor()

if len(argv) <= 1: targetFile = input("Enter file to load: ").replace('\\', '/')
else: targetFile = argv[1].replace('\\', '/')
with open(targetFile) as file: dataframe = pandas.read_json(file, orient="records")
columnname = dataframe.iloc[0][0]
dataframe.columns = dataframe.iloc[0]
dataframe = dataframe.drop(0).dropna().astype(int)
dataframe.to_sql("Loading", conn, index=False, dtype="INTEGER")

preferred = input("Preferred column name: ").lower()
cursor.execute(f"ALTER TABLE Costs ADD COLUMN {preferred} INTEGER")
cursor.execute(f"UPDATE Costs SET {preferred} = (SELECT Loading.{columnname} FROM Loading WHERE Loading.state = Costs.state AND Loading.county = Costs.county)")
cursor.execute("DROP TABLE Loading")
conn.commit()
conn.close()