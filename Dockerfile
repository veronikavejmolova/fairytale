FROM python:3.13

RUN pip install --upgrade pip

WORKDIR /app

COPY fairy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fairy /app/fairy

EXPOSE 8000
ENTRYPOINT ["uvicorn", "fairy.main:app", "--host", "0.0.0.0", "--port", "8000"]
