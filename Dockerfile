FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (e.g., for building some python packages)
# RUN apt-get update && apt-get install -y build-essential

COPY pyproject.toml .
# Copy the rest of the application
COPY . .

# Install dependencies
RUN pip install --no-cache-dir .

EXPOSE 8000

# Run the application
# We use host 0.0.0.0 to make it accessible outside the container
CMD ["adk", "web", ".", "--port", "8000", "--host", "0.0.0.0"]
