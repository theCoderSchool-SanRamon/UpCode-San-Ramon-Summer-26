from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import sqlite3

import api_query as api_query
import property_query as property_query
import listings_query as listings_query

app = FastAPI()

app.add_middleware(  # we should figure this out
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["GET"],
	allow_headers=["*"],
)


@app.get("/census")
def query_census(
	query: str, state: str | None = None, place: str | None = None, county: str | None = None
):
	if place != None and county != None:
		raise HTTPException(
			status_code=422, detail="place and county may not be used together."
		)
	elif place != None or county != None:
		return api_query.CensusRequester().send_query(
			get=query, state=state, place=place, county=county
		)
	else:
		raise HTTPException(status_code=422, detail="place or county must be provided.")


@app.get("/property")
def query_property(address: str = Query(...)):
	return property_query.get_property(address)


@app.get("/listings")
def query_listings(lat: float = Query(...), lon: float = Query(...), radius: float = Query(3.0)):
	return listings_query.get_listings(lat, lon, radius)


if __name__ == "__main__":
	import uvicorn

	uvicorn.run(app, host="0.0.0.0", port=8080)
