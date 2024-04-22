from datetime import datetime, timedelta
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd
from src.database.db import db
from sklearn.model_selection import train_test_split

from src.database.model import User, LocationHistory, InfectionHistory
from src.app import create_patrol_app
import numpy as np

app = create_patrol_app()

session = db.session


# def regression_model_with_ml(latitude_example: float, longitude_example: float, days_back: int):
#     today_date = datetime.now().date()
#     start_date = today_date - timedelta(days=days_back)

    
#     print("Today's Date:", today_date)
#     print("Recent Date for Data:", start_date)

#     query = session.query(
#         LocationHistory.latitude,
#         LocationHistory.longitude,
#         InfectionHistory.infected.label('infected'),
#         LocationHistory.timestamp.label('location_timestamp'),
#         InfectionHistory.timestamp.label('infection_timestamp')
#     ).outerjoin(
#         InfectionHistory, LocationHistory.user_id == InfectionHistory.user_id
#     )
#     # Process data
#     # data = []
#     # for row in query:
#     #     latitude, longitude, infected, location_timestamp, infection_timestamp = row
#     #     infected = infected if infected is not None else False
#     #     timestamp = infection_timestamp if infected else location_timestamp
#     #     days_from_today = (timestamp.date() - today_date).days if timestamp else 0
        
#     #     data.append({
#     #         'latitude': latitude,
#     #         'longitude': longitude,
#     #         'infected': infected,
#     #         'days_from_today': days_from_today
#     #     })

#     # df = pd.DataFrame(data)
#     # print(df)
#     # Filter data for the specified latitude, longitude, and days ahead
#     # location_data = df[(df['latitude'] == latitude_example) & (df['longitude'] == longitude_example) & (df['days_from_today'] == days_ahead)]

#     # # Total number of people expected (assuming each row is a unique visit/person)
#     # total_people = location_data.shape[0]

#     # # Number of infected people
#     # total_infected = location_data['infected'].sum()

#     # # Train a model for future predictions (not shown here due to space, but follows similar procedure as before)
#     # # You might train this model to understand general infection patterns and apply here

#     # print(f"Total people expected at {latitude_example}, {longitude_example} in {days_ahead} days: {total_people}")
#     # print(f"Total infected expected: {total_infected}")
#     data = []
#     for row in query:
#         latitude, longitude, infected, location_timestamp, infection_timestamp = row
#         infected = True if infected is not None else False
#         timestamp = infection_timestamp if infected else location_timestamp
#         days_from_today = (timestamp.date() - today_date).days if timestamp else None

#         data.append({
#             'latitude': latitude,
#             'longitude': longitude,
#             'infected': infected,
#             'timestamp': timestamp.date(),
#             'days_from_today': days_from_today
#         })
#     # df = pd.DataFrame(data)
#     # print(df)
#     # filtered_data = df[(df['latitude'] == latitude_example) & (df['longitude'] == longitude_example) & (df['days_from_today'] >= -days_back)]
#     # print("Filtered Data:", filtered_data)

#     # total_people = filtered_data.shape[0]
#     # total_infected = filtered_data['infected'].sum()

#     # return total_people, total_infected
#     df = pd.DataFrame(data)
#     df = df[df['timestamp'] >= start_date]  # Filter to only include recent data

#     # Feature Engineering
#     df['day_of_week'] = df['timestamp'].apply(lambda x: x.weekday())
#     df['month'] = df['timestamp'].apply(lambda x: x.month)

#     # Prepare features and target
#     features = df[['latitude', 'longitude', 'day_of_week', 'month']]
#     target = df['infected'].astype(int)

#     # Data Splitting
#     X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

#     # Model Pipeline
#     pipeline = Pipeline([
#         ('scaler', StandardScaler()),
#         ('regressor', RandomForestRegressor(n_estimators=100))
#     ])

#     # Model Training
#     pipeline.fit(X_train, y_train)

#     # Prepare input for prediction
#     input_data = pd.DataFrame({
#         'latitude': [latitude_example],
#         'longitude': [longitude_example],
#         'day_of_week': [datetime.now().weekday()],
#         'month': [datetime.now().month]
#     })

#     # Predicting
#     predicted_infections = pipeline.predict(input_data)
#     predicted_infections = np.round(predicted_infections[0]).astype(int)

#     return predicted_infections

def regression_model_with_population_and_infections(latitude_example: float, longitude_example: float, days_back: int):
    today_date = datetime.now().date()
    start_date = today_date - timedelta(days=days_back)

    # Query database
    query = session.query(
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
        infected = True if infected is not None else False
        timestamp = infection_timestamp if infected else location_timestamp
        if timestamp:
            days_from_today = (timestamp.date() - today_date).days
            data.append({
                'latitude': latitude,
                'longitude': longitude,
                'infected': infected,
                'timestamp': timestamp.date(),
                'days_from_today': days_from_today
            })

    df = pd.DataFrame(data)
    df = df[df['timestamp'] >= start_date]  # Use recent data

    # Aggregate data to count total visits and infections per day
    aggregated_data = df.groupby(['latitude', 'longitude', 'timestamp']).agg(
        total_visits=pd.NamedAgg(column="latitude", aggfunc="size"),
        total_infected=pd.NamedAgg(column="infected", aggfunc="sum")
    ).reset_index()

    # Feature Engineering
    aggregated_data['day_of_week'] = aggregated_data['timestamp'].apply(lambda x: x.weekday())
    aggregated_data['month'] = aggregated_data['timestamp'].apply(lambda x: x.month)

    # Prepare features and targets
    features = aggregated_data[['latitude', 'longitude', 'day_of_week', 'month']]
    target_visits = aggregated_data['total_visits']
    target_infected = aggregated_data['total_infected']

    # Data Splitting
    X_train, X_test, y_train_visits, y_test_visits = train_test_split(features, target_visits, test_size=0.2, random_state=42)
    _, _, y_train_infected, y_test_infected = train_test_split(features, target_infected, test_size=0.2, random_state=42)

    # Model Pipelines
    visits_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100))
    ])
    infections_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100))
    ])

    # Model Training
    visits_pipeline.fit(X_train, y_train_visits)
    infections_pipeline.fit(X_train, y_train_infected)

    # Prepare input for prediction
    prediction_date = datetime.now()  # Use current date for features
    input_data = pd.DataFrame({
        'latitude': [latitude_example],
        'longitude': [longitude_example],
        'day_of_week': [prediction_date.weekday()],
        'month': [prediction_date.month]
    })

    # Predicting
    predicted_visits = visits_pipeline.predict(input_data)
    predicted_infections = infections_pipeline.predict(input_data)
    
    return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)


if __name__ == '__main__':
    with app.app_context():
        latitude_example = 34.0118
        longitude_example = -118.4922
        days_back = 30  # Analyze the last 30 days
        predicted_visits, predicted_infections = regression_model_with_population_and_infections(latitude_example, longitude_example, days_back)
        print(f"Predicted Total Visits: {predicted_visits}, Predicted Infections: {predicted_infections}")
