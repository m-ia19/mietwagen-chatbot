# Mietwagen Chatbot – LLM & MCP Demo

This project demonstrates a small chatbot application for automating customer communication in a rental car scenario. It integrates a **Large Language Model (Mistral)** with **MCP tools** and is fully containerized using **Docker**.

---

## Features

- **LLM Integration:** Uses Mistral to interpret user requests in natural language.  
- **MCP Tools:** Provides three tools for rental car operations:
  1. `search_cars` – Search available cars by location and date  
  2. `get_car_details` – Retrieve detailed information for a specific car  
  3. `book_car` – Book a car for a customer  
- **Interactive Prompts:** Requests missing required fields from the user automatically.  
- **Dockerized:** Easy deployment with a single `docker-compose` command.  

---

## Requirements

- Docker & Docker Compose  
- macOS (for test day, as provided by CHECK24)  
- MISTRAL_API_KEY environment variable for LLM integration  

---

## Setup & Run

1. **Clone the repository**
```bash
git clone https://github.com/m-ia19/mietwagen-chatbot.git
cd mietwagen-chatbot

2. **Set Mistral API key**
export MISTRAL_API_KEY="your_api_key_here"

3. **Build Docker image**
docker build -t rental-car-app:latest .

4. **Run the client container**
docker compose run --rm client
- This connects automatically to the server container.
- Interact with the bot in the terminal.
