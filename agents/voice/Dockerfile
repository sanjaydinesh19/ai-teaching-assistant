FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY uvicorn_start.sh ./uvicorn_start.sh
RUN chmod +x ./uvicorn_start.sh

ENV FILE_STORE=/data
EXPOSE 8003
CMD ["./uvicorn_start.sh"]
