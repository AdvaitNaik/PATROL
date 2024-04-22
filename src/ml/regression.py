from pathlib import Path
import pandas as pd
from src.database.db import db
from src.database.model import User, LocationHistory, InfectionHistory
from sqlalchemy.orm import joinedload
from src.app import create_patrol_app
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import create_engine, not_, exists

app = create_patrol_app()

# Assuming db is already configured and session is available
session = db.session

# Query users and their infection records
# def regressionModel():
#     users = session.query(User).all()

#     data = []

#     # Process each user
#     for user in users:
#         # Fetch infection records if any
#         infection_records = user.infection_records.all()  # This fetches dynamically
#         if infection_records:  # Check if there are any records
#             for record in infection_records:
#                 data.append({
#                     'user_id': user.user_id,
#                     'latitude': user.latitude,
#                     'longitude': user.longitude,
#                     'city': user.city,
#                     'symptom_count': len(record.symptoms.split(',')) if record.symptoms else 0,
#                     'infected': record.infected  # True for infected
#                 })
#         else:
#             # No infection records, assume user is not infected
#             data.append({
#                 'user_id': user.user_id,
#                 'latitude': user.latitude,
#                 'longitude': user.longitude,
#                 'city': user.city,
#                 'symptom_count': 0,
#                 'infected': False  # False for not infected
#             })

#     # Create a DataFrame
#     df = pd.DataFrame(data)

#     # Encode categorical data (city)
#     le = LabelEncoder()
#     df['city_encoded'] = le.fit_transform(df['city'].astype(str))

#     # Prepare features and target
#     X = df[['symptom_count', 'latitude', 'longitude', 'city_encoded']]
#     y = df['infected']


#     # Scale the features
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)

#     # Split the data
#     X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

#     # Train the model
#     model = LogisticRegression()
#     model.fit(X_train, y_train)

#     # Prediction
#     predicted = model.predict(X_test)
#     predictions = model.predict_proba(X_test)[:, 1]  # Get the probability of being infected

#     # Calculate metrics
#     accuracy = accuracy_score(y_test, predicted)
#     roc_auc = roc_auc_score(y_test, predictions)

#     print(f"Accuracy: {accuracy}, ROC-AUC: {roc_auc}")

def regressionModel():


    query = session.query(
        User.user_id,
        LocationHistory.latitude,
        LocationHistory.longitude,
        InfectionHistory.infected.label('infected'),
        InfectionHistory.timestamp.label('timestamp')
    ).outerjoin(LocationHistory, User.user_id == LocationHistory.user_id
    ).outerjoin(InfectionHistory, User.user_id == InfectionHistory.user_id)

    # Create dataframe from query
    data = []
    for user_id, latitude, longitude, infected, timestamp in query:
        if infected is None:  # This means no infection record exists for this user
            infected = False

        if latitude is None or longitude is None:  # Check if location data is missing
            continue  
        data.append({
            'latitude': latitude,
            'longitude': longitude,
            'infected': infected,
            'hour': timestamp.hour if timestamp else 0,
            'day': timestamp.weekday() if timestamp else 0
        })

    df = pd.DataFrame(data)
    print("Value Counts", df['infected'].value_counts())

    # Prepare features and target
    X = df[['latitude', 'longitude', 'hour', 'day']]
    y = df['infected']

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

    # Train the model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Prediction and evaluation
    predicted = model.predict(X_test)
    predictions = model.predict_proba(X_test)[:, 1]  # Get the probability of being infected

    # Calculate metrics
    accuracy = accuracy_score(y_test, predicted)
    roc_auc = roc_auc_score(y_test, predictions)

    print(f"Accuracy: {accuracy}, ROC-AUC: {roc_auc}")

if __name__ == '__main__':
    with app.app_context():
        regressionModel()

# Python function regressionModel is designed to use logistic regression to predict infection statuses based on user location and timestamp data.