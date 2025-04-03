from pydantic import BaseModel, Field


class Flight(BaseModel):
    id: int
    source_iata: str = Field(description="Zdrojove letiste", examples=["PRG"])
    target_iata: str = Field(description="Cilove letiste", examples=["BRQ"])
    departure_date: str = Field(description="Datum odletu", examples=["2025-03-27"])
    return_date: str = Field(description="Datum priletu", examples=["2025-03-28"])
    price: float = Field(ge=0.0, description="Cena letenky", examples=[100.0])