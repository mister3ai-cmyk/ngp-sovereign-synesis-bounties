FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY proto/ ./proto/
COPY tests/ ./tests/
COPY Makefile .

RUN make proto

EXPOSE 50051

CMD ["python", "-m", "sila2_hamilton_bridge.server"]