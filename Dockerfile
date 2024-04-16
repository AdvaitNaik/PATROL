# Python 3.10 slim image from Docker Hub
FROM python:3.10-slim-buster

# Set the working directory in the Docker container
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Configure Poetry - Disable the creation of virtual environments because the Docker container itself provides isolation
RUN poetry config virtualenvs.create false

# Copy the project configuration files into the Docker container
COPY pyproject.toml poetry.lock /app/

# Install only main dependencies using Poetry
RUN poetry install --no-dev --no-interaction
RUN poetry add gunicorn

# Copy the rest of your application code into the container
COPY . /app

# Set the command to run your application
CMD ["python3", "main.py"]
# CMD ["gunicorn", "--workers=4", "--bind", "0.0.0.0:5000", "src.app:create_patrol_app"]

# Expose the port gunicorn will run on
EXPOSE 5000
