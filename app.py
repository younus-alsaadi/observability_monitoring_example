import time
import random
from fastapi import FastAPI, Response
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    make_asgi_app,
)

# --- 1. Create the FastAPI App ---
app = FastAPI()

# --- 2. Define Your Metrics ---

# --- THIS IS THE CHANGE (Added "status_code") ---
# Now this counter can track method, endpoint, AND response status
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "endpoint", "status_code"]  # <-- ADDED "status_code"
)

IN_PROGRESS_REQUESTS = Gauge(
    "http_requests_inprogress",
    "Number of in-progress HTTP requests."
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["endpoint"]
)

REQUEST_SUMMARY = Summary(
    "http_request_summary_seconds",
    "HTTP request latency summary in seconds.",
    ["endpoint"]
)


# --- 3. Create Your App Endpoints ---

@app.get("/")
def home():
    IN_PROGRESS_REQUESTS.inc()
    start_time = time.time()
    status_code = 200  # Assume 200 OK

    # Simulate some work
    sleep_time = random.uniform(0.1, 0.6)
    time.sleep(sleep_time)

    endpoint = "/"
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUEST_SUMMARY.labels(endpoint=endpoint).observe(latency)

    IN_PROGRESS_REQUESTS.dec()
    # --- THIS IS THE CHANGE (Added status_code) ---
    REQUESTS_TOTAL.labels(method="GET", endpoint=endpoint, status_code=str(status_code)).inc()
    return Response("Hello from your monitored app!", status_code=status_code)


@app.get("/error")
def error_page():
    IN_PROGRESS_REQUESTS.inc()
    start_time = time.time()

    try:
        if random.random() < 0.5:
            1 / 0  # This will raise an exception
        response_body = "This page works sometimes."
        status_code = 200  # It worked
    except Exception:
        response_body = "Internal Server Error"
        status_code = 500  # It failed

    latency = time.time() - start_time
    endpoint = "/error"
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUEST_SUMMARY.labels(endpoint=endpoint).observe(latency)

    IN_PROGRESS_REQUESTS.dec()

    REQUESTS_TOTAL.labels(method="GET", endpoint=endpoint, status_code=str(status_code)).inc()
    return Response(response_body, status_code=status_code)


# --- 4. Add the /metrics Endpoint ---
# This is what Prometheus will scrape.
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
