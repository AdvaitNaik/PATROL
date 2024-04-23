import numpy as np
from joblib import load
from datetime import datetime, timedelta
import os
from pathlib import Path


FILE_PATH = Path(__file__)
SOURCE_PATH = FILE_PATH.parent.parent
STATIC_PATH = os.path.join(SOURCE_PATH, "static")
VISITS_PIPELINE = os.path.join(STATIC_PATH, "visits_pipeline.joblib")
INFECTIONS_PIPELINE = os.path.join(STATIC_PATH, "infections_pipeline.joblib")

def regression_model(latitude_example: float, longitude_example: float, days_ahead: int):
    visits_pipeline = load(VISITS_PIPELINE)
    infections_pipeline = load(INFECTIONS_PIPELINE)

    prediction_date = datetime.now() + timedelta(days=days_ahead)
    
    input_data = np.array([[latitude_example, longitude_example, prediction_date.weekday(), prediction_date.month]])

    predicted_visits = visits_pipeline.predict(input_data)
    predicted_infections = infections_pipeline.predict(input_data)

    return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)

