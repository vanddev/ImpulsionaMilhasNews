# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

ARG WEBHOOK_URL
ARG BOT_TOKEN
ARG FIREBASE_DB_URL
ARG FIREBASE_CREDENTIAL_LOCATION

ENV WEBHOOK_URL=$WEBHOOK_URL
ENV BOT_TOKEN=$BOT_TOKEN
ENV FIREBASE_DB_URL=$FIREBASE_DB_URL
ENV FIREBASE_CREDENTIAL_LOCATION=$FIREBASE_CREDENTIAL_LOCATION

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Switch to the non-privileged user to run the application.
ENV PATH="/home/appuser/.local/bin:${PATH}"
USER appuser

# Copy the source code into the container.
COPY . /app

RUN pip install --user -r requirements.txt
# Expose the port that the application listens on.
EXPOSE 8000

ENV HYPERCORN_CMD="hypercorn app:app -c hypercorn_config.py -b 0.0.0.0:8000"

# Run the application.
CMD ["sh", "-c", "$HYPERCORN_CMD"]