# Python image to use.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED True

# Set the working directory to /app
WORKDIR /app

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN python -m pip install pip --upgrade
RUN pip install -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
ENTRYPOINT ["hypercorn", "app:app", "--config", "hypercorn.toml"]
