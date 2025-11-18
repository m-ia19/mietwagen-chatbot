#!/usr/bin/env python3
"""
Mietwagen Chatbot (Ollama + MCP)
Pragmatische Version - schnell und einfach
"""

import asyncio
import json
import subprocess
import re
from fastmcp import Client
#import requests
# ============================================================
# LLM Funktion
# ============================================================
def run_llm(prompt: str, model: str = "mistral") -> str:
    """LLM über Ollama CLI aufrufen"""
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=20
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "timeout"
    except Exception as e:
        return f"error"

# ============================================================
# Einfache String-basierte Parameter-Extraktion
# ============================================================
def extract_car_id(text: str) -> str:
    """Extrahiere Auto-ID oder Namen aus Text"""
    text_lower = text.lower()
    
    # Suche nach CAR-ID
    if "car001" in text_lower or "golf" in text_lower:
        return "CAR001"
    if "car002" in text_lower or "bmw" in text_lower or "bmw 3" in text_lower:
        return "CAR002"
    if "car003" in text_lower or "mercedes" in text_lower:
        return "CAR003"
    
    return None

def extract_location(text: str) -> str:
    """Extrahiere Ort aus Text"""
    text_lower = text.lower()
    locations = ["münchen", "berlin", "hamburg", "köln", "düsseldorf", "frankfurt", "stuttgart", "marburg", "augsburg"]
    
    for loc in locations:
        if loc in text_lower:
            return loc.capitalize()
    
    return "München"  # Default

# ============================================================
# Hilfs-Funktionen für schöne Ausgabe
# ============================================================
def extract_json(tool_result) -> dict:
    """Extrahiere JSON aus Tool-Result"""
    try:
        text = tool_result.content[0].text
        return json.loads(text)
    except:
        return {}

def print_search_results(data: dict):
    """Schöne Ausgabe für Autosuche"""
    print(f"\n🔍 Verfügbare Autos in {data.get('location', 'München')}:\n")
    for car in data.get('available_cars', []):
        print(f"  • {car['model']:<20} {car['price_per_day']:>3}€/Tag  (ID: {car['id']})")
    print()

def print_car_details(data: dict):
    """Schöne Ausgabe für Auto-Details"""
    if "error" in data:
        print(f"\n❌ {data['error']}\n")
        return
    
    print(f"\n📋 Details:\n")
    print(f"  Auto:        {data.get('model')}")
    print(f"  Sitze:       {data.get('seats')}")
    print(f"  Preis/Tag:   {data.get('price_per_day')}€")
    print(f"  Getriebe:    {data.get('transmission')}")
    print(f"  Kraftstoff:  {data.get('fuel')}\n")

def print_booking_confirmation(data: dict):
    """Schöne Ausgabe für Buchungsbestätigung"""
    if "error" in data:
        print(f"\n❌ {data['error']}\n")
        return
    
    print(f"\n✅ Buchung erfolgreich!\n")
    print(f"  Buchungsnummer: {data.get('booking_id')}")
    print(f"  Auto:           {data.get('car_model')}")
    print(f"  Kunde:          {data.get('customer')}")
    print(f"  Abholdatum:     {data.get('pickup_date')}\n")

# ============================================================
# MietwagenBot
# ============================================================
class MietwagenBot:
    def __init__(self, client):
        self.client = client

    async def handle_input(self, user_input: str):
        """Verarbeite Nutzer-Input"""
        
        # --- LLM bestimmt Tool (schnell und simpel) ---
        prompt = (
            "Du bist ein Mietwagen-Support-Bot. "
            "Analysiere die Anfrage und benutze das passende Tool für die anfrage des Users. Falls kein Tool passt antworte freundlich und frage nach.\n"
            "Tools: search_cars, get_car_details, book_car\n"
            f"Anfrage: {user_input}"

        
        )
        
        llm_decision = run_llm(prompt).strip().lower()
        
        # Wenn Timeout, versuche zu erraten
        if "timeout" in llm_decision or "error" in llm_decision:
            if any(word in user_input.lower() for word in ["wieviel", "sitze", "details", "infos"]):
                llm_decision = "get_car_details"
            elif any(word in user_input.lower() for word in ["buchen", "buche", "reservieren"]):
                llm_decision = "book_car"
            elif any(word in user_input.lower() for word in ["suche", "autos", "verfügbar", "welche"]):
                llm_decision = "search_cars"
            else:
                print(f"🤖 LLM: Ich verstehe dich nicht ganz. Frag nach Autos, Details oder buchen.\n")
                return
        
        # --- Extrahiere Parameter (einfach) ---
        location = extract_location(user_input)
        car_id = extract_car_id(user_input)
        
        # --- Bestimme welches Tool aufgerufen wird ---
        if "search_cars" in llm_decision:
            print(f"🤖 Suche Autos in {location}...\n")
            result = await self.client.call_tool("search_cars", {
                "location": location,
                "start_date": "2025-12-01",
                "end_date": "2025-12-05"
            })
            data = extract_json(result)
            print_search_results(data)

        elif "get_car_details" in llm_decision:
            if not car_id:
                print(f"🤖 Welches Auto? (VW Golf, BMW 3, Mercedes E)\n")
                return
            
            print(f"🤖 Details für {car_id}...\n")
            result = await self.client.call_tool("get_car_details", {
                "car_id": car_id
            })
            data = extract_json(result)
            print_car_details(data)

        elif "book_car" in llm_decision:
            if not car_id:
                print(f"🤖 Welches Auto möchtest du buchen? (VW Golf, BMW 3, Mercedes E)\n")
                return
            
            print(f"🤖 Buche {car_id}...\n")
            result = await self.client.call_tool("book_car", {
                "car_id": car_id,
                "customer_name": "Max Mustermann",
                "start_date": "2025-12-01"
            })
            data = extract_json(result)
            print_booking_confirmation(data)

        else:
            print(f"🤖 {llm_decision}\n")

# ============================================================
# Main
# ============================================================
async def main():
    print("\n" + "="*50)
    print("🚗 CHECK24 Mietwagen-Bot")
    print("="*50)
    print("Tippen Sie: 'exit' zum Beenden\n")

    async with Client("server.py") as client:
        bot = MietwagenBot(client)
        while True:
            try:
                user_input = input("👤 Du: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\n✅ Auf Wiedersehen!\n")
                    break
                
                await bot.handle_input(user_input)
            except KeyboardInterrupt:
                print("\n✅ Auf Wiedersehen!\n")
                break
            except Exception as e:
                print(f"❌ Fehler: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())