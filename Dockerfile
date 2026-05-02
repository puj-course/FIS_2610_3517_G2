FROM python:3.10-slim

RUN useradd -m prueba

WORKDIR /app

COPY --chown=myuser:myuser backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=prueba:prueba backend/ .

USER prueba
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
