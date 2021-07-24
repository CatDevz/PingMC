FROM python:3.9

RUN pip install fastapi uvicorn

EXPOSE 8080

COPY ./app /app

CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "8080"]
