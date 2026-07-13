from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import sqlite3

import api_query


app = FastAPI()

app.add_middleware(  # we should figure this out
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["GET"],
	allow_headers=["*"],
)



if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)
