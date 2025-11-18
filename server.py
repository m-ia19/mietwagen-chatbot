#!/usr/bin/env python3
"""
MCP Server für Mietwagen-Tools
Nutzt FastMCP - die neueste und einfachste API
"""

import json
from fastmcp import FastMCP

# ============================================================
# Initialisiere FastMCP Server
# ============================================================
server = FastMCP("rental-car-server")

# ============================================================
# Fake Datenbank
# ============================================================
CARS = {
    "CAR001": {"model": "VW Golf", "price": 45, "seats": 5},
    "CAR002": {"model": "BMW 3", "price": 85, "seats": 5},
    "CAR003": {"model": "Mercedes E", "price": 120, "seats": 5},
}

# ============================================================
# TOOL 1: Search Cars
# ============================================================
@server.tool()
def search_cars(location: str, start_date: str, end_date: str) -> str:
    """Suche verfügbare Mietwagen an einem Ort"""
    print(f"🔍 Suche Autos in {location} von {start_date} bis {end_date}")
    available = []
    for car_id, details in CARS.items():
        available.append({
            "id": car_id,
            "model": details["model"],
            "price_per_day": details["price"]
        })
    return json.dumps({"location": location, "available_cars": available})


# ============================================================
# TOOL 2: Get Car Details
# ============================================================
@server.tool()
def get_car_details(car_id: str) -> str:
    """Hole detaillierte Infos über ein Auto"""
    print(f"📋 Hole Details für {car_id}")
    car = CARS.get(car_id)
    if not car:
        return json.dumps({"error": f"Auto {car_id} nicht gefunden"})
    return json.dumps({
        "car_id": car_id,
        "model": car["model"],
        "price_per_day": car["price"],
        "seats": car["seats"],
        "transmission": "automatic",
        "fuel": "diesel"
    })


# ============================================================
# TOOL 3: Book Car
# ============================================================
@server.tool()
def book_car(car_id: str, customer_name: str, start_date: str) -> str:
    """Buche ein Auto für einen Kunden"""
    print(f"✅ Buche {car_id} für {customer_name} ab {start_date}")
    if car_id not in CARS:
        return json.dumps({"error": "Auto nicht vorhanden"})
    booking_id = f"BK{car_id}{start_date.replace('-', '')}"
    return json.dumps({
        "status": "booked",
        "booking_id": booking_id,
        "car_model": CARS[car_id]["model"],
        "customer": customer_name,
        "pickup_date": start_date
    })


# ============================================================
# Server starten
# ============================================================
if __name__ == "__main__":
    print("🚀 MCP Server startet...")
    print("Verfügbare Tools:")
    print("  - search_cars")
    print("  - get_car_details")
    print("  - book_car")
    print("\nWartet auf Verbindungen...\n")

    #server.run(transport="http", port=11434) 
    server.run(transport="http", host="0.0.0.0", port=11434)
  