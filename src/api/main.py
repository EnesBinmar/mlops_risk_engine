import fastapi
import uvicorn
import joblib
from contextlib import asynccontextmanager
from pathlib import Path
#contextlib python standart kütüphanesidir.

ROOT_DIR = Path(__file__).parent.parent.parent
print(ROOT_DIR)
best_threshold = joblib.load(ROOT_DIR/"notebooks"/"best_threshold.pkl")

@asynccontextmanager
async def lifespan(app: FastAPI):
    #uygulama çalışmaya başladığında çalışan kısım
    artifact_path = ROOT_DIR / "notebooks" / "best_threshol.pkl"
    app.state.best_threshold = joblib.load(artifact_path)
    #app.state nesnesi ile yüklenen değişken yaşam döngüsünde kalıcı kalır bir kez yüklenir hep kalır 
    yield

    # -- SHUTDOWN (Uygulama kapanırken çalışan uygulamalar)
    pass
app = FastAPI(lifespan=lifespan)
