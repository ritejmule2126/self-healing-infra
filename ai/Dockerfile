FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY prediction_api.py auto_healer.py model.pkl scaler.pkl ./
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["gunicorn","--bind","0.0.0.0:8000","prediction_api:app"]
