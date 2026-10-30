import fastapi
import uvicorn
import joblib
from contextlib import asynccontextmanager
from pathlib import Path
#contextlib python standart kütüphanesidir.

ROOT_DIR = Path(__file__).parent.parent.parent
print(ROOT_DIR)
#best_threshold = joblib.load(".. /notebooks/best_threshold.pkl")
#async def lifespan():
