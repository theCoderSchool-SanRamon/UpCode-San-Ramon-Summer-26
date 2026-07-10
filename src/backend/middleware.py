from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import sqlite3

import src.backend.census_query as census_query


def load_local_headers():
	with sqlite3.connect("census.db") as conn:
		cursor = conn.cursor()
		global county_headers
		county_headers = [
			x[1] for x in cursor.execute("PRAGMA table_info(Costs)").fetchall()
		]
		global place_headers
		place_headers = [
			x[1]
			for x in cursor.execute("PRAGMA table_info(PlaceAttributes)").fetchall()
		]


app = FastAPI()

app.add_middleware(  # we should figure this out
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["GET"],
	allow_headers=["*"],
)


@app.get("/census/place")
def census_place(place: str, state: str, query: str):
	return census_query.query_place(place, state, query)


@app.get("/census/county")
def census_county(county: str, state: str, query: str):
	return census_query.query_county(county, state, query)


@app.get("/local/complete/place")
def local_complete_place(place: str, state: str):
	with sqlite3.connect("census.db") as conn:
		cursor = conn.cursor()
		return dict(
			zip(
				place_headers,
				cursor.execute(
					"SELECT * FROM PlaceAttributes WHERE state = ? AND place = ?",
					(int(state), int(place)),
				).fetchone(),
			)
		)


@app.get("/local/complete/county")
def local_complete_county(county: str, state: str):
	with sqlite3.connect("census.db") as conn:
		cursor = conn.cursor()
		return dict(
			zip(
				county_headers,
				cursor.execute(
					"SELECT * FROM Costs WHERE state = ? AND county = ?",
					(int(state), int(county)),
				).fetchone(),
			)
		)


load_local_headers()

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
