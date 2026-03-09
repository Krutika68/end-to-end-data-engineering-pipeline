import random
from datetime import datetime
from fastapi import FastAPI, HTTPException

app = FastAPI()

instruments = ["AAPL", "BTC-USD", "ETH-USD", "TSLA"]


@app.get("/v1/market-data")
def get_market_data():
    
    # Fault Injection (5% chance)
    if random.random() < 0.05:
        if random.choice([True, False]):
            raise HTTPException(status_code=500, detail="Injected API failure")
        else:
            return [{"instrument_id": "AAPL", "price": "INVALID"}]

    data = []

    for _ in range(5):
        instrument = random.choice(instruments)

        record = {
            "instrument_id": instrument,
            "price": round(random.uniform(100, 50000), 2),
            "volume": round(random.uniform(1, 1000), 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        data.append(record)

    return data