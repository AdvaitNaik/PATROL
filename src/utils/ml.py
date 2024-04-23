

from src.database.model import LocationHistory, InfectionHistory
from src.database.db import db
from joblib import dump
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from src.app import create_patrol_app

app = create_patrol_app()

from joblib import load
import pandas as pd
from datetime import datetime, timedelta


def regression_model(latitude_example: float, longitude_example: float, days_ahead: int):
    # Load models
    visits_pipeline = load('visits_pipeline.joblib')
    infections_pipeline = load('infections_pipeline.joblib')

    # Calculate the future date
    prediction_date = datetime.now() + timedelta(days=days_ahead)
    
    input_data = pd.DataFrame({
        'latitude': [latitude_example],
        'longitude': [longitude_example],
        'day_of_week': [prediction_date.weekday()],
        'month': [prediction_date.month]
    })

    # Predict using the future date's attributes
    predicted_visits = visits_pipeline.predict(input_data)
    predicted_infections = infections_pipeline.predict(input_data)

    return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)


def train_and_save_model():
    # Assume db.session is set up correctly and imported
    query = db.session.query(
        LocationHistory.latitude,
        LocationHistory.longitude,
        InfectionHistory.infected.label('infected'),
        LocationHistory.timestamp.label('location_timestamp'),
        InfectionHistory.timestamp.label('infection_timestamp')
    ).outerjoin(
        InfectionHistory, LocationHistory.user_id == InfectionHistory.user_id
    )

    data = []
    for row in query:
        latitude, longitude, infected, location_timestamp, infection_timestamp = row
        infected = infected is not None
        timestamp = infection_timestamp if infected else location_timestamp
        if timestamp:
            data.append({
                'latitude': latitude,
                'longitude': longitude,
                'infected': infected,
                'timestamp': timestamp.date()
            })

    df = pd.DataFrame(data)

    aggregated_data = df.groupby(['latitude', 'longitude', 'timestamp']).agg(
        total_visits=pd.NamedAgg(column="latitude", aggfunc="size"),
        total_infected=pd.NamedAgg(column="infected", aggfunc="sum")
    ).reset_index()

    aggregated_data['day_of_week'] = aggregated_data['timestamp'].apply(lambda x: x.weekday())
    aggregated_data['month'] = aggregated_data['timestamp'].apply(lambda x: x.month)

    features = aggregated_data[['latitude', 'longitude', 'day_of_week', 'month']]
    targets = aggregated_data[['total_visits', 'total_infected']]

    X_train, _, y_train, _ = train_test_split(features, targets, test_size=0.2, random_state=42)

    visits_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100))
    ])
    infections_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100))
    ])

    # Fit models
    visits_pipeline.fit(X_train, y_train['total_visits'])
    infections_pipeline.fit(X_train, y_train['total_infected'])

    # Save models
    dump(visits_pipeline, 'visits_pipeline.joblib')
    dump(infections_pipeline, 'infections_pipeline.joblib')

if __name__ == "__main__":
    with app.app_context():
        train_and_save_model()
