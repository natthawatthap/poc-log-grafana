from fastapi import FastAPI, Request
from prometheus_client import Counter, Summary, generate_latest
from starlette.responses import Response
from logging_loki import LokiHandler
import logging
import time

app = FastAPI()

# Loki Configuration
LOKI_URL = "http://localhost:3100/loki/api/v1/push"  # Update to match your Loki instance

try:
    loki_handler = LokiHandler(
        url=LOKI_URL,
        tags={"application": "fastapi-app"},
        version="1",
    )
    logger = logging.getLogger("loki_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(loki_handler)
    logger.info("Loki logging initialized successfully")
except Exception as e:
    logger = logging.getLogger("fallback_logger")
    logger.setLevel(logging.WARNING)
    logger.warning(f"Failed to initialize Loki logging. Logs will not be sent to Loki. Error: {e}")

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint"]
)
REQUEST_LATENCY = Summary(
    "http_request_latency_seconds", "Latency of HTTP requests"
)
ITEM_COUNTER = Counter(
    "item_requests_total", "Count of item requests", ["item_id"]
)

# Middleware to track request count and latency
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    # Increment Prometheus request counter
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    # Log incoming request
    logger.info(f"Incoming request: method={method}, endpoint={endpoint}")

    start_time = time.time()
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        # Log exception
        logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
        raise exc
    finally:
        # Log request latency to Prometheus and Loki
        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)
        logger.info(f"Request latency: {latency:.4f} seconds for {method} {endpoint}")

# A simple root route
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to FastAPI with Prometheus and Loki!"}

# Another route with custom metrics
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    # Increment Prometheus custom item counter
    ITEM_COUNTER.labels(item_id=str(item_id)).inc()

    # Log item access
    logger.info(f"Item endpoint accessed with item_id={item_id}")
    return {"item_id": item_id, "status": "requested"}

# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    metrics_data = generate_latest()
    logger.info("Metrics endpoint accessed")
    return Response(content=metrics_data, media_type="text/plain")
