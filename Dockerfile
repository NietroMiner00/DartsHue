# Use a slim Buster-slim image for ARM architecture
FROM arm32v7/python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy pyproject.toml and uv.lock (if using uv) first to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install uv && uv sync

# Copy the rest of the application code
COPY . .

# Expose any necessary ports (if your application listens on one)
# For example, if it's a web server: EXPOSE 80

# Run the main application
CMD ["python", "main.py"]