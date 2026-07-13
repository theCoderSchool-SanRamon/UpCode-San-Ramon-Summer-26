from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import sqlite3

import api_query as api_query


app = FastAPI()

app.add_middleware(  # we should figure this out
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["GET"],
	allow_headers=["*"],
)

@app.get("/census")
def query_census(get: str, state: int, place: int | None = None, county: int | None = None):
	return api_query.CensusRequester().send_query(get=get, state=state, place=place, county=county)

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)
