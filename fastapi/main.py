from fastapi import FastAPI, HTTPException
from typing import List
from model import Flight


app = FastAPI()


flights_db: List[Flight] = []


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Flight API"}


@app.get("/flights", response_model=List[Flight], tags=["Flights"])
def read_flights():
    return flights_db


@app.get("/flights/{flight_id}", response_model=Flight, tags=["Flights"])
def get_flight(flight_id: int):
    for flight in flights_db:
        if flight.id == flight_id:
            return flight
    raise HTTPException(status_code=404, detail="Flight not found")


@app.post("/flights", response_model=Flight, tags=["Flights"])
def create_flight(flight: Flight):
    flights_db.append(flight)
    return flight


@app.delete("/flights/{flight_id}", tags=["Flights"])
def delete_flight(flight_id: int):
    for index, flight in enumerate(flights_db):
        if flight.id == flight_id:
            del flights_db[index]
            return {"message": "Flight deleted successfully"}
    raise HTTPException(status_code=404, detail="Flight not found")