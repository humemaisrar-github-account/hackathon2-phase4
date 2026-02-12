# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code into the container at /app
COPY . .

# Create the database and tables on container startup
# This command should ideally be run as part of the entrypoint script
# or as a separate migration step in a production environment.
# For simplicity in this Dockerfile, we'll ensure it runs before the app starts.
# We'll use a wrapper script to do this.

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Define environment variable for SQLALCHEMY_DATABASE_URL
ENV SQLALCHEMY_DATABASE_URL="sqlite:///./sql_app.db"

# Command to run the application with Uvicorn
# We'll create a startup script to run create_db_and_tables() first
COPY ./start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["./start.sh"]
