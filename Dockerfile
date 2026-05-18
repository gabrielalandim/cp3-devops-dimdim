FROM python:3.10-slim

WORKDIR /app_dimdim

COPY requirements.txt .
COPY app.py .

RUN pip install --no-cache-dir -r requirements.txt

ENV AMBIENTE=producao
ENV PORTA=5000

RUN useradd -m dimdimuser && chown -R dimdimuser /app_dimdim
USER dimdimuser

EXPOSE 5000

CMD ["python", "app.py"]