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


# import onnxruntime as ort
# import numpy as np
# from datetime import datetime, timedelta
# import os
# from pathlib import Path

# FILE_PATH = Path(__file__)
# SOURCE_PATH = FILE_PATH.parent.parent
# STATIC_PATH = os.path.join(SOURCE_PATH, "static")
# VISITS_PIPELINE = os.path.join(STATIC_PATH, "visits_pipeline.onnx")
# INFECTIONS_PIPELINE = os.path.join(STATIC_PATH, "infections_pipeline.onnx")

# def load_model(model_path):
#     sess = ort.InferenceSession(model_path)
#     return sess

# def regression_model(latitude_example: float, longitude_example: float, days_ahead: int):
#     visits_pipeline = load_model(VISITS_PIPELINE)
#     infections_pipeline = load_model(INFECTIONS_PIPELINE)

#     prediction_date = datetime.now() + timedelta(days=days_ahead)
#     input_data = np.array([[latitude_example, longitude_example, prediction_date.weekday(), prediction_date.month]], dtype=np.float32)

#     input_name_visits = visits_pipeline.get_inputs()[0].name
#     predicted_visits = visits_pipeline.run(None, {input_name_visits: input_data})[0]

#     input_name_infections = infections_pipeline.get_inputs()[0].name
#     predicted_infections = infections_pipeline.run(None, {input_name_infections: input_data})[0]

#     return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)

from src.database.model import LocationHistory, VaccinationHistory, InfectionHistory
from src.database.db import db
from datetime import datetime, timedelta
import xgboost as xgb
import numpy as np
from pathlib import Path
import os

FILE_PATH = Path(__file__)
SOURCE_PATH = FILE_PATH.parent.parent
STATIC_PATH = os.path.join(SOURCE_PATH, "static")
VISITS_PIPELINE = os.path.join(STATIC_PATH, "visits_pipeline.bst")
INFECTIONS_PIPELINE = os.path.join(STATIC_PATH, "infections_pipeline.bst")

# def train_and_save_model():
#     # Assuming db.session and the necessary model imports are set up correctly
#     query = db.session.query(
#         LocationHistory.latitude,
#         LocationHistory.longitude,
#         InfectionHistory.infected.label('infected'),
#         LocationHistory.timestamp.label('location_timestamp'),
#         InfectionHistory.timestamp.label('infection_timestamp')
#     ).outerjoin(
#         InfectionHistory, LocationHistory.user_id == InfectionHistory.user_id
#     )

#     aggregated_data = {}
#     for row in query:
#         latitude, longitude, infected, location_timestamp, infection_timestamp = row
#         infected = infected is not None
#         timestamp = infection_timestamp if infected else location_timestamp

#         if timestamp:
#             key = (latitude, longitude, timestamp.date().weekday(), timestamp.date().month)
#             if key not in aggregated_data:
#                 aggregated_data[key] = {'total_visits': 0, 'total_infected': 0}
#             aggregated_data[key]['total_visits'] += 1
#             aggregated_data[key]['total_infected'] += int(infected)

#     # Prepare data for model
#     feature_list = []
#     target_visits = []
#     target_infected = []
#     for key, value in aggregated_data.items():
#         feature_list.append([key[0], key[1], key[2], key[3]])  # lat, long, day_of_week, month
#         target_visits.append(value['total_visits'])
#         target_infected.append(value['total_infected'])

#     # Convert lists to DMatrix
#     dtrain_visits = xgb.DMatrix(data=np.array(feature_list), label=np.array(target_visits))
#     dtrain_infected = xgb.DMatrix(data=np.array(feature_list), label=np.array(target_infected))

#     ### Step 2: Set up XGBoost parameters and train models
#     params = {
#         'max_depth': 3,
#         'eta': 0.1,
#         'objective': 'reg:squarederror',
#         'eval_metric': 'rmse'
#     }

#     visits_bst = xgb.train(params, dtrain_visits, num_boost_round=100)
#     infections_bst = xgb.train(params, dtrain_infected, num_boost_round=100)

#     ### Step 3: Save the trained models
#     visits_bst.save_model('visits_pipeline.bst')
#     infections_bst.save_model('infections_pipeline.bst')

def load_model(model_path):
    bst = xgb.Booster()
    bst.load_model(model_path)
    return bst

def regression_model(latitude_example: float, longitude_example: float, days_ahead: int):
    # train_and_save_model()

    visits_pipeline = load_model(VISITS_PIPELINE)
    infections_pipeline = load_model(INFECTIONS_PIPELINE)

    prediction_date = datetime.now() + timedelta(days=days_ahead)
    input_data = np.array([[latitude_example, longitude_example, prediction_date.weekday(), prediction_date.month]])

    dtest = xgb.DMatrix(input_data)

    predicted_visits = visits_pipeline.predict(dtest)
    predicted_infections = infections_pipeline.predict(dtest)

    return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)
