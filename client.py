import asyncio
import json
from fastmcp import Client
from mistralai import Mistral
import os
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:11434/mcp")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
mistral = Mistral(api_key=MISTRAL_API_KEY)

SYSTEM_PROMPT = """
You are an autonomous agent that can use MCP tools.
Whenever it helps the user, call an MCP tool.
Fill in missing parameters automatically without asking the user.
Available tools: search_cars(location, start_date, end_date), get_car_details(car_id), book_car(car_id, customer_name, start_date)
"""

async def main():
    async with Client(MCP_SERVER_URL) as mcp:
        print("Connected to MCP server!")

        while True:
            user_input = input("User: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                break

            # Step 1: Ask Mistral what to do
            llm_response = mistral.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ]
            )

            msg = llm_response.choices[0].message

            # Step 2: If the LLM wants to call a tool
            if msg.tool_calls:
                call = msg.tool_calls[0]
                tool_name = call.function.name
                args = json.loads(call.function.arguments)

                print(f"🛠 Calling MCP tool {tool_name} with args {args}")
                result = await mcp.call_tool(tool_name, args)
                print("Tool result:", result.data)

                # Step 3: Give tool result back to LLM for a nice reply
                final_response = mistral.chat.complete(
                    model="mistral-small-latest",
                    messages=[
                        {"role": "system", "content": "Convert the tool result to a helpful answer."},
                        {"role": "user", "content": user_input},
                        {"role": "tool", "content": json.dumps(result.data)}
                    ]
                )
                print("Assistant:", final_response.choices[0].message.content)
            else:
                # LLM did not call a tool, just respond normally
                print("Assistant:", msg.content)

if __name__ == "__main__":
    asyncio.run(main())
