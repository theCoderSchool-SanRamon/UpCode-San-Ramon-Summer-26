from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import census_query

app = FastAPI()

app.add_middleware( #we should figure this out
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get('/census/place')
def census_place(place:str,state:str,query:str):
	print("e")
	data = census_query.query(place,state,query)
	return data

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
