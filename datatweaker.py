import sqlite3, json


class DataTweaker:
	"""A class specifically intended to modify countydata.js."""

	def __init__(self):
		self.conn = sqlite3.connect("census.db")
		self.cursor = self.conn.cursor()
		with open("countydata.js") as file:
			self.data = json.loads(file.readline()[24:])

	def __enter__(self):
		return self

	def __exit__(self):
		self.conn.close()

	def insert_data(self, position: str, query: str):
		"""Pulls data into this object's buffer to be inserted into countydata.js.
		position -- JavaScript-alike object path: "name" or "subdict.name".
				Subdicts must exist already. Use insert_subdict("subdict") first.
		query -- the name of the column in census.db to query.
				Will cause an error if the column does not exist for security reasons.
		"""
		if not query in [
			x[1] for x in self.cursor.execute("PRAGMA table_info(Costs)").fetchall()
		]:
			raise AttributeError(name=query, obj=self)
		position_path = position.split(".")
		for i in self.data.keys():
			self.cursor.execute(
				f'SELECT "{query}" FROM Costs WHERE Costs.countyname = ? AND Costs.statename = ?',
				(i.split("_")[0], i.split("_")[1]),
			)
			item = self.cursor.fetchone()
			if item != None:
				item = item[0]
			exec(
				f'self.data["{i}"]'
				+ "".join(['["' + x + '"]' for x in position_path])
				+ " = item"
			)

	def insert_subdict(self, position: str):
		"""Creates a subdict.
		position -- JavaScript-alike object path: "subdict" or "subdict.subsubdict"."""
		position_path = position.split(".")
		for i in self.data.keys():
			exec(
				f'self.data["{i}"]'
				+ "".join(['["' + x + '"]' for x in position_path])
				+ " = {}"
			)

	def preview_data(self, position: int = 0):
		"""Prints the entry at position."""
		print(self.data[tuple(self.data.keys())[position]])

	def commit_data(self):
		"""Writes data from this object's buffer to countydata.js."""
		with open("countydata.js", "w") as file:
			file.write("const countyProperties = " + json.dumps(self.data))
