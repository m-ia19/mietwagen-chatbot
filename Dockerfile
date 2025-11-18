# Start with Python 3.12 on a small Linux system
FROM python:3.12-slim

# Set working directory INSIDE the container
# Think: "cd /app" but in the container
WORKDIR /app

# Copy requirements.txt from your computer INTO the container
# Format: COPY [from your computer] [to inside container]
COPY requirements.txt .

# Install Python packages inside the container
# The dot (.) means "in the current directory" (/app)
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python code into the container
COPY server.py .
COPY client.py .

# Tell Docker this container will listen on port 11434
# (This doesn't actually open it, just documents it)
EXPOSE 11434

# When container starts, run this command
# This starts your MCP server
CMD ["python", "server.py"]