FROM python:3.12-slim

# TODO: remove me
ENV PATH="/root/.local/bin:${PATH}"

RUN apt-get update && \
    apt-get install -y curl git nodejs npm && \
    apt-get clean

RUN pip install poetry
RUN poetry config virtualenvs.create false
