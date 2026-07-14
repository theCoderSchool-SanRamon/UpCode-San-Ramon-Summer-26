from fastapi import FastAPI, Query, HTTPException
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
def query_census(
	get: str, state: int, place: int | None = None, county: int | None = None
):
	if place != None and county != None:
		raise HTTPException(
			status_code=422, detail="place and county may not be used together."
		)
	elif place != None:
		return api_query.CensusRequester().send_query(
			get=get, state=str(state), place=str(place)
		)
	elif county != None:
		return api_query.CensusRequester().send_query(
			get=get, state=str(state), county=str(county)
		)
	else:
		raise HTTPException(status_code=422, detail="place or county must be provided.")


if __name__ == "__main__":
	import uvicorn

	uvicorn.run(app, host="0.0.0.0", port=8000)
