from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://devuser:devpassword@localhost:5432/devdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return { "msg": "Hello!", "Docker": "0.1" }

@app.get("/api/ip")
async def get_ip(request: Request):
    return {"ip": request.client.host}

@app.get("/ip", response_class=HTMLResponse)
async def get_ip_html(request: Request):
    return f"<h1>Your IP: {request.client.host}</h1>"

# Hotel API endpoints

@app.get("/rooms")
def get_rooms():
    with SessionLocal() as session:
        result = session.execute(text("""
            SELECT id, room_number, price_per_night
            FROM rooms
        """))
        rooms = [{"id": row[0], "name": row[1], "price_per_night": float(row[2])} for row in result]
        return rooms

@app.get("/bookings")
def get_bookings():
    with SessionLocal() as session:
        result = session.execute(text("""
            SELECT
                b.id AS booking_id,
                g.name AS guest_name,
                r.room_number,
                EXTRACT(day FROM b.date_to - b.date_from)::int AS nights,
                EXTRACT(day FROM b.date_to - b.date_from)::int * r.price_per_night AS total_price,
                b.date_from,
                b.date_to
            FROM bookings b
            INNER JOIN guests g ON b.guest_id = g.id
            INNER JOIN rooms r ON b.room_id = r.id
        """))
        bookings = [{
            "booking_id": row[0],
            "guest_name": row[1],
            "room_number": row[2],
            "nights": row[3],
            "total_price": float(row[4]),
            "date_from": str(row[5]),
            "date_to": str(row[6])
        } for row in result]
        return bookings

@app.get("/guests")
def get_guests():
    with SessionLocal() as session:
        result = session.execute(text("""
            SELECT
                g.id AS guest_id,
                g.name,
                COALESCE((
                    SELECT COUNT(*)
                    FROM bookings AS b
                    WHERE b.guest_id = g.id
                      AND b.date_to < CURRENT_DATE
                ), 0) AS visits_count
            FROM guests AS g
        """))
        guests = [{
            "guest_id": row[0],
            "name": row[1],
            "visits_count": row[2]
        } for row in result]
        return guests

@app.post("/bookings")
def create_booking(booking: dict):
    with SessionLocal() as session:
        session.execute(text("""
            INSERT INTO bookings (guest_id, room_id, date_from, date_to)
            VALUES (:guest_id, :room_id, :date_from, :date_to)
        """), {
            "guest_id": booking["guest_id"],
            "room_id": booking["room_id"],
            "date_from": booking["date_from"],
            "date_to": booking["date_to"]
        })
        session.commit()
        return {"message": "Booking created"}

# Temporary rooms endpoint for compatibility
@app.get("/api/rooms")
def get_api_rooms():
    return get_rooms()

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

@app.get("/time")
def get_time():
    return {"time": datetime.now().isoformat()}

