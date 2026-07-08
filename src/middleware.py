from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware( #we should figure this out
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get('city')
def city(id):
	# there'd be some stuff with sqlite here probably
	return ...

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
