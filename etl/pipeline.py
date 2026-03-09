import requests
import psycopg2
import time
from datetime import datetime
from pydantic import BaseModel, ValidationError
import os

API_URL = "http://api:8000/v1/market-data"

DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "market")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")


class MarketData(BaseModel):
    instrument_id: str
    price: float
    volume: float
    timestamp: datetime


def fetch_data():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("API request failed:", e)
        return []


def calculate_vwap(records):
    total_price_volume = sum(r.price * r.volume for r in records)
    total_volume = sum(r.volume for r in records)
    return total_price_volume / total_volume if total_volume else 0


def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def run_pipeline():

    start = time.time()

    raw_data = fetch_data()

    valid_records = []
    dropped = 0

    for record in raw_data:
        try:
            validated = MarketData(**record)
            valid_records.append(validated)
        except ValidationError:
            dropped += 1

    if not valid_records:
        print("No valid records")
        return

    avg_price = sum(r.price for r in valid_records) / len(valid_records)

    vwap = calculate_vwap(valid_records)

    conn = connect_db()
    cursor = conn.cursor()

    processed = 0

    for r in valid_records:

        # Outlier detection
        if abs(r.price - avg_price) / avg_price > 0.15:
            print("Outlier detected:", r.instrument_id)

        try:
            cursor.execute(
                """
                INSERT INTO market_data (instrument_id, price, volume, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (r.instrument_id, r.price, r.volume, r.timestamp)
            )

            processed += 1

        except Exception as e:
            print("Insert error:", e)

    conn.commit()
    cursor.close()
    conn.close()

    end = time.time()

    print("Records Processed:", processed)
    print("Records Dropped:", dropped)
    print("VWAP:", round(vwap, 2))
    print("Execution Time:", round(end - start, 2), "seconds")


if __name__ == "__main__":
    run_pipeline()