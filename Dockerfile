# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends ffmpeg git
RUN pip install --upgrade pip setuptools wheel pipenv
RUN pipenv install --system --deploy --ignore-pipfile

CMD exec python main.py