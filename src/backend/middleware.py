from fastapi import FastAPI, Query, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import api_query as api_query
import property_query as property_query
import listings_query as listings_query
import streetview_query as streetview_query
import gemini_query as gemini_query

app = FastAPI()

app.add_middleware(  # we should figure this out
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["GET", "POST"],
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


@app.get("/streetview")
def query_streetview(lat: float = Query(...), lng: float = Query(...)):
	return streetview_query.get_streetview_meta(lat, lng)


@app.get("/streetview/img")
def query_streetview_img(lat: float = Query(...), lng: float = Query(...), size: str = Query(streetview_query.DEFAULT_SIZE)):
	return streetview_query.get_streetview_image(lat, lng, size)


@app.post("/chat")
def query_chat(payload: dict = Body(...)):
	return gemini_query.get_chat_reply(payload)


if __name__ == "__main__":
	import uvicorn

	uvicorn.run(app, host="0.0.0.0", port=8080)
