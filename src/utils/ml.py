# from datetime import datetime, timedelta
# from sklearn.pipeline import Pipeline
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.preprocessing import StandardScaler
# import pandas as pd
# from src.database.db import db
# from sklearn.model_selection import train_test_split

# from src.database.model import LocationHistory, InfectionHistory
# import numpy as np


# def fetch_data(start_date):
#     today_date = datetime.now().date()
#     query = db.session.query(
#         LocationHistory.latitude,
#         LocationHistory.longitude,
#         InfectionHistory.infected.label('infected'),
#         LocationHistory.timestamp.label('location_timestamp'),
#         InfectionHistory.timestamp.label('infection_timestamp')
#     ).outerjoin(
#         InfectionHistory, LocationHistory.user_id == InfectionHistory.user_id
#     )

#     data = []
#     for row in query:
#         latitude, longitude, infected, location_timestamp, infection_timestamp = row
#         infected = infected is not None
#         timestamp = infection_timestamp if infected else location_timestamp
#         if timestamp:
#             days_from_today = (timestamp.date() - today_date).days
#             data.append({
#                 'latitude': latitude,
#                 'longitude': longitude,
#                 'infected': infected,
#                 'timestamp': timestamp.date(),
#                 'days_from_today': days_from_today
#             })
#     return data


# def prepare_dataframe(data, start_date):
#     df = pd.DataFrame(data)
#     df = df[df['timestamp'] >= start_date]

#     aggregated_data = df.groupby(['latitude', 'longitude', 'timestamp']).agg(
#         total_visits=pd.NamedAgg(column="latitude", aggfunc="size"),
#         total_infected=pd.NamedAgg(column="infected", aggfunc="sum")
#     ).reset_index()

#     aggregated_data['day_of_week'] = aggregated_data['timestamp'].apply(lambda x: x.weekday())
#     aggregated_data['month'] = aggregated_data['timestamp'].apply(lambda x: x.month)
#     return aggregated_data


# def train_models(aggregated_data):
#     features = aggregated_data[['latitude', 'longitude', 'day_of_week', 'month']]
#     target_visits = aggregated_data['total_visits']
#     target_infected = aggregated_data['total_infected']

#     X_train, X_test, y_train_visits, y_test_visits = train_test_split(features, target_visits, test_size=0.2, random_state=42)
#     _, _, y_train_infected, y_test_infected = train_test_split(features, target_infected, test_size=0.2, random_state=42)

#     visits_pipeline = Pipeline([
#         ('scaler', StandardScaler()),
#         ('regressor', RandomForestRegressor(n_estimators=100))
#     ])
#     infections_pipeline = Pipeline([
#         ('scaler', StandardScaler()),
#         ('regressor', RandomForestRegressor(n_estimators=100))
#     ])

#     visits_pipeline.fit(X_train, y_train_visits)
#     infections_pipeline.fit(X_train, y_train_infected)

#     return visits_pipeline, infections_pipeline


# def make_predictions(visits_pipeline, infections_pipeline, latitude, longitude):
#     prediction_date = datetime.now()
#     input_data = pd.DataFrame({
#         'latitude': [latitude],
#         'longitude': [longitude],
#         'day_of_week': [prediction_date.weekday()],
#         'month': [prediction_date.month]
#     })

#     predicted_visits = visits_pipeline.predict(input_data)
#     predicted_infections = infections_pipeline.predict(input_data)
    
#     return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)


# def regression_model(latitude: float, longitude: float, days_back: int):
#     today_date = datetime.now().date()
#     start_date = today_date - timedelta(days=days_back)

#     data = fetch_data(start_date)
#     aggregated_data = prepare_dataframe(data, start_date)
#     visits_pipeline, infections_pipeline = train_models(aggregated_data)
#     predicted_visits, predicted_infections = make_predictions(visits_pipeline, infections_pipeline, latitude, longitude)

#     return predicted_visits, predicted_infections
