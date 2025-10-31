# app.py
import time
import random
from flask import Flask, Response
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    make_wsgi_app,
)

# --- 1. Create the Flask App ---
app = Flask(__name__)

# --- 2. Define Your Metrics ---
# We use four main metric types.

# COUNTER: A value that only goes up (e.g., total requests)
# We add "labels" to split the data by 'method' and 'endpoint'.
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "endpoint"]
)

# GAUGE: A value that can go up or down (e.g., current active users)
IN_PROGRESS_REQUESTS = Gauge(
    "http_requests_inprogress",
    "Number of in-progress HTTP requests."
)

# HISTOGRAM: Tracks the distribution of values (e.g., request latency)
# It creates "buckets" (e.g., <0.1s, <0.2s, <0.5s) and counts how many
# requests fall into each. Great for calculating percentiles (e.g., 95th).
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["endpoint"]
)

# SUMMARY: Similar to Histogram, but calculates quantiles on the client.
# Use Histogram most of the time. Summary is for special cases.
REQUEST_SUMMARY = Summary(
    "http_request_summary_seconds",
    "HTTP request latency summary in seconds.",
    ["endpoint"]
)


# --- 3. Create Your App Endpoints ---

@app.route("/")
def home():
    IN_PROGRESS_REQUESTS.inc()  # Increment gauge
    start_time = time.time()

    # Simulate some work
    sleep_time = random.uniform(0.1, 0.6)
    time.sleep(sleep_time)

    endpoint = "/"
    # Record the latency in the Histogram and Summary
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUEST_SUMMARY.labels(endpoint=endpoint).observe(latency)

    IN_PROGRESS_REQUESTS.dec()  # Decrement gauge
    REQUESTS_TOTAL.labels(method="GET", endpoint=endpoint).inc()  # Increment counter
    return "Hello from your monitored app!"


@app.route("/error")
def error_page():
    IN_PROGRESS_REQUESTS.inc()
    start_time = time.time()

    try:
        # Simulate a random failure
        if random.random() < 0.5:
            1 / 0  # This will raise an exception
        response_body = "This page works sometimes."
        status_code = 200
    except Exception:
        response_body = "Internal Server Error"
        status_code = 500

    latency = time.time() - start_time
    endpoint = "/error"
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUEST_SUMMARY.labels(endpoint=endpoint).observe(latency)

    IN_PROGRESS_REQUESTS.dec()
    REQUESTS_TOTAL.labels(method="GET", endpoint=endpoint).inc()
    return response_body, status_code


# --- 4. Add the /metrics Endpoint ---
# This is what Prometheus will scrape.
# We use the 'make_wsgi_app' from the prometheus_client library.
app.wsgi_app = make_wsgi_app(app.wsgi_app)

if __name__ == "__main__":
    # Run the app on port 5000 and make it accessible
    # from outside the container (host='0.0.0.0')
    app.run(host="0.0.0.0", port=5001)