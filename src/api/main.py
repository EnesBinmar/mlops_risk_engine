import fastapi
from fastapi import FastAPI, Request
import uvicorn
import joblib
from contextlib import asynccontextmanager
from pathlib import Path
import numpy as np
import tensorflow as tf

ROOT_DIR = Path(__file__).parent.parent.parent
print(ROOT_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # TensorFlow/Keras modeli ve joblib ile kaydedilmiş scaler/threshold dosyalarının yüklenmesi
    app.state.best_threshold = joblib.load(ROOT_DIR / "notebooks" / "best_threshold.pkl")
    app.state.model = tf.keras.models.load_model(ROOT_DIR / "best_dnn_model.keras")
    app.state.scalerAmount = joblib.load(ROOT_DIR / "notebooks" / "robust_scaler_amount.pkl")
    app.state.scalerTime = joblib.load(ROOT_DIR / "notebooks" / "robust_scaler_time.pkl")
    
    yield

    # -- SHUTDOWN
    pass

app = FastAPI(lifespan=lifespan)

@app.post("/predict")
async def predict(data: DataModel, request: Request):
    input_data = np.array([[
        data.Time, data.V1, data.V2, data.V3, data.V4, data.V5, 
        data.V6, data.V7, data.V8, data.V9, data.V10, data.V11, 
        data.V12, data.V13, data.V14, data.V15, data.V16, data.V17, 
        data.V18, data.V19, data.V20, data.V21, data.V22, data.V23, 
        data.V24, data.V25, data.V26, data.V27, data.V28, data.Amount
    ]])
    
    scaled_amount = request.app.state.scalerAmount.transform([[data.Amount]])
    scaled_time = request.app.state.scalerTime.transform([[data.Time]])
    
    # Time (0. indeks) ve Amount (29. indeks) değerlerini scale edilmiş halleriyle güncelleme
    input_data[0, 0] = scaled_time[0, 0]
    input_data[0, 29] = scaled_amount[0, 0]

    # Keras modeli ile çıkarım (Inference)
    # Keras .predict() metodu ikili sınıflandırmada (sigmoid) shape: (1, 1) döner.
    preds = request.app.state.model.predict(input_data)
    fraud_probability = float(preds[0][0])
    
    # Best threshold değerine göre sınıf tahmini yapma
    prediction = int(fraud_probability >= request.app.state.best_threshold)
    
    return {
        "fraud_probability": fraud_probability,
        "prediction": prediction  
    }