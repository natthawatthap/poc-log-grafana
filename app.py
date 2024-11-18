from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager

# Create the app
app = FastAPI()

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Define the lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup any other startup tasks here if needed
    yield
    # Cleanup tasks can be added here

# Pass the lifespan handler to the app
app.router.lifespan = lifespan

# Define endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
