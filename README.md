# End-to-End Data Engineering & Infrastructure Challenge

This project implements a simple data pipeline consisting of:

1. **Source (API)** – A FastAPI service that generates synthetic market data.
2. **Pipeline (ETL)** – A Python pipeline that extracts, validates, transforms, and loads data.
3. **Sink (Database)** – A PostgreSQL database storing processed records.

The entire system is containerized using Docker and orchestrated with Docker Compose.

---

# Setup Instructions

## Prerequisites
- Docker
- Docker Compose

## Run the System

Clone the repository and run:
```bash
docker-compose up --build
```

This command will start:
- FastAPI API server
- PostgreSQL database
- ETL pipeline service

---

# API Endpoint

GET /v1/market-data

Returns a list of market data objects containing:

- instrument_id
- price
- volume
- timestamp

The API includes **fault injection**, where 5% of requests return either a 500 error or malformed data to test ETL resilience.

---

# ETL Pipeline

The ETL pipeline performs:

### Extraction
Polls the API and handles network errors and faulty responses.

### Transformation
- Calculates **VWAP (Volume Weighted Average Price)** for each instrument.
- Flags **outliers** where the price deviates more than 15% from the batch average.

### Quality Control
- **Schema validation** using Pydantic.
- Prevents duplicate records using `(instrument_id, timestamp)`.
- Logs records processed, records dropped, and execution time.

---

# System Design

## 1. Scaling

If the system needed to process **1 billion events per day**, the architecture could be extended using:

- **Apache Kafka** for high-throughput event streaming.
- **Apache Spark or Flink** for distributed data processing.
- **Cloud-based storage and distributed databases** to scale horizontally.

This would allow the system to handle large-scale data ingestion and processing.

---

## 2. Monitoring

Health checks can be implemented using:

- A `/health` endpoint in the API.
- Docker container health checks.
- Monitoring tools such as **Prometheus and Grafana** to track system performance and failures.

This ensures the pipeline and services are running correctly in production.

---

## 3. Recovery (Idempotency)

To prevent partial or duplicate data if the pipeline fails during a batch:

- Use **unique constraints** on `(instrument_id, timestamp)` in PostgreSQL.
- Use **database transactions** to avoid partial writes.
- Implement **checkpointing** so the pipeline can resume from the last successful record.

This ensures reliable and consistent data processing.
