FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir piper-tts

RUN mkdir -p /models /media

COPY docker/piper/piper_server.py /workspace/piper_server.py

EXPOSE 8080

CMD ["python", "piper_server.py"]