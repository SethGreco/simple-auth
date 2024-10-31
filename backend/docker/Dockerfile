FROM python:3.12-slim

ENV PATH="/root/.local/bin:${PATH}"

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean

WORKDIR /backend/

RUN pip3 install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml /backend

COPY logging.yml /backend

RUN poetry install --only main

COPY /qftb /backend/qftb/

EXPOSE 8000

ENTRYPOINT [ \
    "/usr/local/bin/uvicorn", \
    "--host=0.0.0.0", \
    "--log-config=logging.yml", \
    "qftb.main:app" \
    ]
