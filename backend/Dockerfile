FROM python:3.12-slim

WORKDIR /backend

RUN pip install poetry

COPY . .

EXPOSE 8000

RUN poetry config virtualenvs.create false

RUN poetry install

CMD ["poetry", "run", "uvicorn", "--reload", "--host", "0.0.0.0", "--port", "8000","api.main:app"]

