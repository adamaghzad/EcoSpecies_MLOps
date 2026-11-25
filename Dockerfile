FROM python:3.12-slim
WORKDIR /app
COPY requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt
COPY eco ./eco
COPY config.json .
COPY artifacts/champion.joblib ./artifacts/champion.joblib
RUN useradd --uid 10001 --create-home appuser && mkdir /app/.state && chown -R appuser /app
USER appuser
EXPOSE 8000
CMD ["python","-m","uvicorn","eco.api:app","--host","0.0.0.0","--port","8000"]
