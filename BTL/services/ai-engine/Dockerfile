FROM alpine:latest

RUN apk add --no-cache python3 py3-pip py3-pillow py3-numpy

RUN pip install --no-cache-dir fastapi uvicorn networkx requests python-multipart --break-system-packages

WORKDIR /app

COPY app ./app

EXPOSE 8005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
