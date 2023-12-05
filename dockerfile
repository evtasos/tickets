FROM python:3.8-slim-buster

# Install DNS utilities and OpenSSL
RUN apt-get update && apt-get install -y dnsutils openssl

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Generate a self-signed certificate
RUN openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=GR/L=Local/O=Dev/CN=tickets.metaxa"

# Make port 443 available to the world outside this container
EXPOSE 5556

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5556", "--certfile=cert.pem", "--keyfile=key.pem", "app:app"]
