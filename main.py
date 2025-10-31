import time
import random
import asyncio  # We'll use this for non-blocking sleep
from fastapi import FastAPI
from starlette.responses import Response, JSONResponse
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    generate_latest, CONTENT_TYPE_LATEST,
)

# --- 1. Create the FastAPI App ---
app = FastAPI()

# --- 2. Define Your Metrics ---
# This is identical to the Flask app, but we'll add 'http_status'
# to our counter, which is very useful.

# COUNTER
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "endpoint", "http_status"]
)

# GAUGE
IN_PROGRESS_REQUESTS = Gauge(
    "http_requests_inprogress",
    "Number of in-progress HTTP requests."
)

# HISTOGRAM
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["endpoint"]
)

# SUMMARY
REQUEST_SUMMARY = Summary(
    "http_request_summary_seconds",
    "HTTP request latency summary in seconds.",
    ["endpoint"]
)


# --- 3. Create Your App Endpoints ---
# FastAPI uses async/await syntax, which is great for performance.

@app.get("/")
async def home():
    IN_PROGRESS_REQUESTS.inc()
    start_time = time.time()
    endpoint = "/"
    status_code = 200

    try:
        # Simulate some async work
        sleep_time = random.uniform(0.1, 0.6)
        await asyncio.sleep(sleep_time)

        response_body = {"message": "Hello from your monitored app!"}

    finally:
        latency = time.time() - start_time
        IN_PROGRESS_REQUESTS.dec()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        REQUESTS_TOTAL.labels(method="GET", endpoint=endpoint, http_status=status_code).inc()

    return response_body


@app.get("/error")
async def error_page():
    IN_PROGRESS_REQUESTS.inc()
    start_time = time.time()
    endpoint = "/error"

    try:
        # Simulate a random failure
        if random.random() < 0.5:
            1 / 0  # This will raise an exception

        response_body = {"message": "This page works sometimes."}
        status_code = 200
        return response_body

    except Exception:
        response_body = {"message": "Internal Server Error"}
        status_code = 500
        # FastAPI uses JSONResponse to set custom status codes
        return JSONResponse(content=response_body, status_code=status_code)

    finally:
        latency = time.time() - start_time
        IN_PROGRESS_REQUESTS.dec()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        REQUESTS_TOTAL.labels(method="GET", endpoint=endpoint, http_status=status_code).inc()


# --- 4. Add the /metrics Endpoint ---
# This is the new part for FastAPI. We create a simple
# endpoint that returns the latest metrics text.
@app.get("/metrics")
async def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


