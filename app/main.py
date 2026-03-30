from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse

app = FastAPI()

orgins = ["*"]  # Allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=orgins,  # Allow all origins
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return { "msg": "Hello!", "Docker": "0.1" }


@app.get("/api/ip")
async def get_ip(request: Request):
    return {"ip": request.client.host}

@app.get("/ip", response_class=HTMLResponse)
def ip(request: Request):
    return f"<h1>ip {request.client.host}</h1>"

@app.get("/hello")
def hello():
    return { "msg": "Hello Max"}


@app.get("/rooms")
def get_rooms():
    return rooms

@app.get("/rooms/{room_number}")
def get_room(room_number: int):
    for room in rooms:
        if room["room_number"] == room_number:
            return room
    return {"error": "Room not found"}
