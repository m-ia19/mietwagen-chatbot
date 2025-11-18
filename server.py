import os
import json
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from mistralai import Mistral

# -------------------------------
# Load Mistral API key
# -------------------------------
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY not set in .env")

mistral = Mistral(api_key=MISTRAL_API_KEY)

# -------------------------------
# FastMCP server HTTP endpoint
# -------------------------------
MCP_SERVER_URL = "http://server:11434/mcp"

# -------------------------------
# Required parameters per tool
# -------------------------------
REQUIRED_PARAMS = {
    "search_cars": ["location", "start_date", "end_date"],
    "get_car_details": ["car_id"],
    "book_car": ["car_id", "customer_name", "start_date"]
}

# -------------------------------
# Pretty-print tool responses
# -------------------------------
def print_tool_response(tool_name, response, params=None):
    try:
        data = json.loads(response.data)
        if tool_name == "search_cars" and "available_cars" in data:
            print(f"\n🤖 Available cars in {data['location']} from {params.get('start_date')} to {params.get('end_date')}:")
            for car in data["available_cars"]:
                print(f" - {car['model']} (ID: {car['id']}), Price: €{car['price_per_day']}/day")
        elif tool_name == "get_car_details":
            print(f"\n🤖 Car details for {data['car_id']}:")
            print(f" Model: {data['model']}")
            print(f" Price/day: €{data['price_per_day']}")
            print(f" Seats: {data['seats']}")
            print(f" Transmission: {data['transmission']}")
            print(f" Fuel: {data['fuel']}")
        elif tool_name == "book_car":
            print(f"\n🤖 Booking confirmed!")
            print(f" Booking ID: {data['booking_id']}")
            print(f" Car: {data['car_model']}")
            print(f" Customer: {data['customer']}")
            print(f" Pickup date: {data['pickup_date']}")
        else:
            print("\n🤖 Tool Response:", data)
    except Exception:
        print("\n🤖 Tool Response (raw):", response)

# -------------------------------
# Main interactive client
# -------------------------------
async def main():
    try:
        # Wait for server to be ready
        await asyncio.sleep(5)

        async with Client(MCP_SERVER_URL) as client:
            print("🚀 Connected to FastMCP server!")
            print("Welcome! Ask about rental cars. Type 'exit' to quit.\n")

            while True:
                user_input = input("👤 You: ").strip()
                if user_input.lower() in ("exit", "quit"):
                    print("Goodbye! 👋")
                    break

                # -------------------------------
                # Prompt Mistral to decide which tool to call
                # -------------------------------
                tool_prompt = f"""
You are a friendly rental-car assistant. Decide which MCP tool to call: search_cars, get_car_details, book_car.
Always consider the **conversation context**. If the user asked something previously, incorporate that information.
Output a valid JSON with all required fields for the tool.
If any required field is missing, ask the user for it interactively.
If no tool fits the user input, respond in a friendly way explaining what you can help with.

User input: "{user_input}"
Output format: TOOL:<tool_name> PARAMS:<json> or FRIENDLY_NO_TOOL:<text>
"""

                try:
                    decision = mistral.chat.complete(
                        model="mistral-small-latest",
                        messages=[{"role": "user", "content": tool_prompt}]
                    )
                    decision_text = decision.choices[0].message.content.strip()
                except Exception as e:
                    print("⚠️ Mistral API error:", e)
                    continue

                # -------------------------------
                # Tool call handling
                # -------------------------------
                if decision_text.startswith("TOOL:"):
                    try:
                        _, rest = decision_text.split("TOOL:", 1)
                        tool_name, params_part = rest.split("PARAMS:", 1)
                        tool_name = tool_name.strip()
                        params = json.loads(params_part.strip() or "{}")

                        # Validate required parameters
                        missing = [p for p in REQUIRED_PARAMS.get(tool_name, []) if p not in params]
                        for param in missing:
                            params[param] = input(f"Please enter {param}: ").strip()

                        # Print “friendly tool call” style
                        print(f"\n🚗🔍 Let me search for available cars right away!")
                        print(f"*Calling tool: `{tool_name}({', '.join(f'{k}={json.dumps(v)}' for k,v in params.items())})`...*\n")

                        # Call MCP tool
                        tool_response = await client.call_tool(tool_name, params)
                        print_tool_response(tool_name, tool_response, params)

                    except Exception as e:
                        print("⚠️ Error parsing Mistral response or calling tool:", e)

                # -------------------------------
                # Friendly no-tool response
                # -------------------------------
                elif decision_text.startswith("FRIENDLY_NO_TOOL:"):
                    friendly_msg = decision_text.split("FRIENDLY_NO_TOOL:", 1)[1].strip()
                    print("\n🤖 Mistral:", friendly_msg)

                # -------------------------------
                # Fallback: just print Mistral reply
                # -------------------------------
                else:
                    print("\n🤖 Mistral:", decision_text)

    except Exception as e:
        print("⚠️ Failed to connect to FastMCP server:", e)

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    asyncio.run(main())
