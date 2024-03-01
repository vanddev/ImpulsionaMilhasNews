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
ARG FIREBASE_SDK_TOKEN

ENV WEBHOOK_URL=$WEBHOOK_URL
ENV BOT_TOKEN=$BOT_TOKEN
ENV FIREBASE_DB_URL=$FIREBASE_DB_URL
ENV FIREBASE_SDK_TOKEN=$FIREBASE_SDK_TOKEN

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
#ARG UID=10001
#RUN adduser \
#    --disabled-password \
#    --gecos "" \
#    --home "/nonexistent" \
#    --shell "/sbin/nologin" \
#    --no-create-home \
#    --uid "${UID}" \
#    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
#RUN --mount=type=cache,target=/root/.cache/pip \
#    --mount=type=bind,source=requirements.txt,target=requirements.txt \
#    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
#USER appuser

# Copy the source code into the container.
COPY . /app

RUN pip install -r requirements.txt
# Expose the port that the application listens on.
EXPOSE 8000

ENV HYPERCORN_CMD="hypercorn app:app -c hypercorn_config.py -b 0.0.0.0:8000"

# Run the application.
CMD ["sh", "-c", "$HYPERCORN_CMD"]
#
#CMD ["python", "main.py"]