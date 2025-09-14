import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

# 1. Initialize FastAPI app
app = FastAPI(
    title="IoT Sensor Analytics API",
    description="An API to serve simulated sensor data and basic analytics.",
    version="1.0.0"
)

# 2. Configure CORS
# This is crucial! It allows our React frontend (running on a different port)
# to make requests to this backend.
origins = [
    "http://localhost:5173", # Default Vite/React port
    "http://localhost:3000", # Common alternative for React dev server
    "https://iot-frontend-iota-six.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# 3. Data Simulation Function
def simulate_sensor_data(num_records: int = 100):
    """Generates a DataFrame of simulated IoT sensor data."""
    # Create a date range for our timestamps
    timestamps = pd.to_datetime(pd.date_range(end=pd.Timestamp.now(), periods=num_records, freq='T'))
    
    # Generate random data
    data = {
        'timestamp': timestamps,
        'sensor_id': np.random.choice(['sensor_alpha', 'sensor_beta', 'sensor_gamma'], num_records),
        'temperature': np.random.normal(loc=22.5, scale=2.0, size=num_records),
        'humidity': np.random.normal(loc=55.0, scale=5.0, size=num_records),
    }
    return pd.DataFrame(data)

# 4. Pydantic models for structured responses (good practice!)
# This helps with type hinting, validation, and auto-documentation.
class AnalyticsResult(BaseModel):
    total_records: int
    average_temp: float
    max_temp: float
    min_temp: float
    average_humidity: float
    records_per_sensor: Dict[str, int]
    raw_data: List[Dict]


# 5. Define the API Endpoint
@app.get("/api/v1/analytics", response_model=AnalyticsResult)
def get_analytics_data():
    """
    This endpoint simulates new sensor data, performs calculations,
    and returns a structured JSON response.
    """
    # Step A: Simulate fresh data every time the endpoint is called
    df = simulate_sensor_data(num_records=150)

    # Step B: Perform calculations using Pandas
    analytics = {
        "total_records": len(df),
        "average_temp": round(df['temperature'].mean(), 2),
        "max_temp": round(df['temperature'].max(), 2),
        "min_temp": round(df['temperature'].min(), 2),
        "average_humidity": round(df['humidity'].mean(), 2),
        "records_per_sensor": df['sensor_id'].value_counts().to_dict(),
    }

    # Step C: Format the raw data for clean JSON output
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['temperature'] = df['temperature'].round(2)
    df['humidity'] = df['humidity'].round(2)
    raw_data_for_json = df.to_dict(orient='records')

    # Step D: Combine and return the final payload
    return {**analytics, "raw_data": raw_data_for_json}

# 6. Add a root endpoint for a simple health check
@app.get("/")
def read_root():
    return {"status": "OK", "message": "Welcome to the IoT Analytics Backend!"}