FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install uv
RUN uv venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
RUN uv pip install -r requirements.txt


COPY . .

