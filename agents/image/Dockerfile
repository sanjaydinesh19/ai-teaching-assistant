FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and fonts
COPY app ./app
COPY app/assets/fonts ./app/assets/fonts

COPY uvicorn_start.sh ./uvicorn_start.sh
RUN chmod +x ./uvicorn_start.sh

ENV FILE_STORE=/data
EXPOSE 8002
CMD ["./uvicorn_start.sh"]
