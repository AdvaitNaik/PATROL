# import numpy as np
# from joblib import load
# from datetime import datetime, timedelta
# import os
# from pathlib import Path


# FILE_PATH = Path(__file__)
# SOURCE_PATH = FILE_PATH.parent.parent
# STATIC_PATH = os.path.join(SOURCE_PATH, "static")
# VISITS_PIPELINE = os.path.join(STATIC_PATH, "visits_pipeline.joblib")
# INFECTIONS_PIPELINE = os.path.join(STATIC_PATH, "infections_pipeline.joblib")

# def regression_model(latitude_example: float, longitude_example: float, days_ahead: int):
#     visits_pipeline = load(VISITS_PIPELINE)
#     infections_pipeline = load(INFECTIONS_PIPELINE)

#     prediction_date = datetime.now() + timedelta(days=days_ahead)
    
#     input_data = np.array([[latitude_example, longitude_example, prediction_date.weekday(), prediction_date.month]])

#     predicted_visits = visits_pipeline.predict(input_data)
#     predicted_infections = infections_pipeline.predict(input_data)

#     return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)


import onnxruntime as ort
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path

FILE_PATH = Path(__file__)
SOURCE_PATH = FILE_PATH.parent.parent
STATIC_PATH = os.path.join(SOURCE_PATH, "static")
VISITS_PIPELINE = os.path.join(STATIC_PATH, "visits_pipeline.onnx")
INFECTIONS_PIPELINE = os.path.join(STATIC_PATH, "infections_pipeline.onnx")

def load_model(model_path):
    sess = ort.InferenceSession(model_path)
    return sess

def regression_model(latitude_example: float, longitude_example: float, days_ahead: int):
    visits_pipeline = load_model(VISITS_PIPELINE)
    infections_pipeline = load_model(INFECTIONS_PIPELINE)

    prediction_date = datetime.now() + timedelta(days=days_ahead)
    input_data = np.array([[latitude_example, longitude_example, prediction_date.weekday(), prediction_date.month]], dtype=np.float32)

    input_name_visits = visits_pipeline.get_inputs()[0].name
    predicted_visits = visits_pipeline.run(None, {input_name_visits: input_data})[0]

    input_name_infections = infections_pipeline.get_inputs()[0].name
    predicted_infections = infections_pipeline.run(None, {input_name_infections: input_data})[0]

    return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)




