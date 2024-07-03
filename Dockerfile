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
ENTRYPOINT ["python", "-m", "quart", "run", "--host=0.0.0.0", "--port=8080"]

# CMD exec gunicorn --bind :$PORT --workers 4 --threads 1 --timeout 0 app:app
# CMD exec gunicorn app:app
# ENTRYPOINT ["gunicorn", "app:app", "-c", "gunicorn.conf.py"]
