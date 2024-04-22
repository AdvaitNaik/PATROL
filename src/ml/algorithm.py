from pathlib import Path
import pandas as pd
from src.database.db import db
from src.database.model import User, LocationHistory, InfectionHistory
from sqlalchemy.orm import joinedload
from src.app import create_patrol_app
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.compose import ColumnTransformer

app = create_patrol_app()

session = db.session

def regressionModel():

    query = session.query(
    LocationHistory.user_id,
    LocationHistory.latitude,
    LocationHistory.longitude,
    InfectionHistory.infected.label('infected'),
    LocationHistory.timestamp.label('location_timestamp'),  # Fetch from LocationHistory
    InfectionHistory.timestamp.label('infection_timestamp')  # Fetch from InfectionHistory if available
    ).outerjoin(
        InfectionHistory, LocationHistory.user_id == InfectionHistory.user_id
    )

    # Now let's process the fetched data
    data = []
    for row in query:
        user_id, latitude, longitude, infected, location_timestamp, infection_timestamp = row
        if infected is None:
            infected = False
            timestamp = location_timestamp  # Use location timestamp if no infection record
        else:
            timestamp = infection_timestamp  # Use infection timestamp if record exists

        data.append({
            'user_id': user_id,
            'latitude': latitude,
            'longitude': longitude,
            'infected': infected,
            'hour': timestamp.hour if timestamp else 0,
            'day': timestamp.weekday() if timestamp else 0
        })

    df = pd.DataFrame(data)
    print(df)


    # Feature Engineering
    df['infected'] = df['infected'].astype(int)  # Convert boolean to int

    # Split the data into features and targets
    X = df[['latitude', 'longitude', 'hour', 'day']]
    y_class = df['infected']

    y_regress = df.groupby(['latitude', 'longitude', 'day']).size().reset_index(name='count')

    X_y_regress = pd.merge(X, y_regress, on=['latitude', 'longitude', 'day'], how='left').fillna(0)

    # Split data for training and testing
    X_train, X_test, y_train_class, y_test_class = train_test_split(X, y_class, test_size=0.2, random_state=42)
    X_train_regress, X_test_regress, y_train_regress, y_test_regress = train_test_split(X_y_regress[['latitude', 'longitude', 'day']], X_y_regress['count'], test_size=0.2, random_state=42)

    # Model pipeline
    classifier_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100))
    ])
    regressor_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100))
    ])

    # Fit models
    classifier_pipeline.fit(X_train, y_train_class)
    regressor_pipeline.fit(X_train_regress, y_train_regress)

    # Predict and evaluate
    y_pred_class = classifier_pipeline.predict(X_test)
    y_pred_regress = regressor_pipeline.predict(X_test_regress)

    classification_accuracy = accuracy_score(y_test_class, y_pred_class)
    regression_error = mean_squared_error(y_test_regress, y_pred_regress)

    print(f'Classification Accuracy: {classification_accuracy}')
    print(f'Regression Mean Squared Error: {regression_error}')

    latitude_example = 34.0567
    longitude_example = -118.2917
    day_example = 5
    hour_example = 14  # Assuming an hour if it wasn't given, as your model requires this feature

    # Create a DataFrame for the input data with all required features
# Ensure only the features used in training are included for prediction
    input_data_regression = pd.DataFrame({
        'latitude': [latitude_example],
        'longitude': [longitude_example],
        'day': [day_example]
    })

    # Predicting infection status might still use the 'hour', so keep it separate
    input_data_classification = pd.DataFrame({
        'latitude': [latitude_example],
        'longitude': [longitude_example],
        'hour': [14],  
        'day': [day_example]
    })

    # Use the classifier and regressor pipelines properly
    infected_status_prediction = classifier_pipeline.predict(input_data_classification)
    user_count_prediction = regressor_pipeline.predict(input_data_regression)

    # Output the predictions
    print(f"Predicted Infection Status (0 for not infected, 1 for infected): {infected_status_prediction[0]}")
    print(f"Predicted Number of Users on Day {day_example}: {int(user_count_prediction[0])}")



if __name__ == '__main__':
    with app.app_context():
        regressionModel()
