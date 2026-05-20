FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if required by underlying libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the default Streamlit port
EXPOSE 49281

# Healthcheck to verify Streamlit is running
HEALTHCHECK CMD curl --fail http://localhost:49281/_stcore/health || exit 1

# Command to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=49281", "--server.address=0.0.0.0"]
