import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
from src.database.db import db
from src.database.model import LocationHistory, InfectionHistory
from sqlalchemy.orm import joinedload

FILE_PATH = Path(__file__)
SOURCE_PATH = FILE_PATH.parent.parent
STATIC_PATH = os.path.join(SOURCE_PATH, "static")
VISITS_PIPELINE = os.path.join(STATIC_PATH, 'visits_model.npy')
INFECTIONS_PIPELINE = os.path.join(STATIC_PATH, 'infections_model.npy')

class RandomForestRegressorCustom:
   def __init__(self, n_estimators=100):
       self.n_estimators = n_estimators
       self.trees = []

   def fit(self, X, y):
       for _ in range(self.n_estimators):
           indices = np.random.choice(X.shape[0], size=X.shape[0], replace=True)
           X_subset, y_subset = X[indices], y[indices]
           tree = DecisionTreeRegressorCustom()
           tree.fit(X_subset, y_subset)
           self.trees.append(tree)

   def predict(self, X):
       predictions = np.zeros(X.shape[0])
       for tree in self.trees:
           predictions += tree.predict(X)
       return predictions / self.n_estimators


class DecisionTreeRegressorCustom:
   def __init__(self, max_depth=None):
       self.max_depth = max_depth

   def fit(self, X, y):
       self.tree = self._build_tree(X, y, depth=0)

   def _build_tree(self, X, y, depth):
       if len(set(y)) == 1 or depth == self.max_depth:
           return np.mean(y)

       feature_index, split_value = self._find_best_split(X, y)

       if feature_index is None:
           return np.mean(y)

       left_indices = X[:, feature_index] <= split_value
       right_indices = ~left_indices

       left_tree = self._build_tree(X[left_indices], y[left_indices], depth + 1)
       right_tree = self._build_tree(X[right_indices], y[right_indices], depth + 1)

       return {'feature_index': feature_index, 'split_value': split_value,
               'left_tree': left_tree, 'right_tree': right_tree}

   def _find_best_split(self, X, y):
       best_score = float('inf')
       best_feature_index = None
       best_split_value = None

       for feature_index in range(X.shape[1]):
           unique_values = np.unique(X[:, feature_index])
           for value in unique_values:
               left_indices = X[:, feature_index] <= value
               right_indices = ~left_indices

               if len(y[left_indices]) == 0 or len(y[right_indices]) == 0:
                   continue

               mse = self._calculate_mse(y[left_indices], y[right_indices])
               if mse < best_score:
                   best_score = mse
                   best_feature_index = feature_index
                   best_split_value = value

       return best_feature_index, best_split_value

   def _calculate_mse(self, left_y, right_y):
       left_mean = np.mean(left_y)
       right_mean = np.mean(right_y)
       total_samples = len(left_y) + len(right_y)
       return (np.sum((left_y - left_mean) ** 2) + np.sum((right_y - right_mean) ** 2)) / total_samples

   def predict(self, X):
       return np.array([self._predict_tree(x, self.tree) for x in X])

   def _predict_tree(self, x, tree):
       if isinstance(tree, (float, np.float64)):
           return tree
       if x[tree['feature_index']] <= tree['split_value']:
           return self._predict_tree(x, tree['left_tree'])
       else:
           return self._predict_tree(x, tree['right_tree'])

# def fetch_and_prepare_data():
#     query = db.session.query(
#         LocationHistory.latitude,
#         LocationHistory.longitude,
#         LocationHistory.timestamp,
#         InfectionHistory.infected
#     ).outerjoin(
#         InfectionHistory, LocationHistory.user_id == InfectionHistory.user_id
#     )

#     data = []
#     for row in query:
#         latitude, longitude, timestamp, infected = row
#         infected = 1 if infected else 0  # Convert boolean to int (True to 1, False to 0)
#         day_of_week = timestamp.weekday()
#         month = timestamp.month
#         total_visits = 1  # Assuming each row represents one visit
#         data.append([latitude, longitude, day_of_week, month, total_visits, infected])

#     return np.array(data)

# def train_and_save_model():
#    # Assume data is a numpy array with columns latitude, longitude, day_of_week, month, total_visits, total_infected
#    data = fetch_and_prepare_data()

#    # Separate features and targets
#    features = data[:, :4]
#    targets = data[:, 4:]

#    # Fit models
#    visits_model = RandomForestRegressorCustom(n_estimators=100)
#    visits_model.fit(features, targets[:, 0])

#    infections_model = RandomForestRegressorCustom(n_estimators=100)
#    infections_model.fit(features, targets[:, 1])

#    # Save models
#    np.save('visits_model.npy', visits_model)
#    np.save('infections_model.npy', infections_model)


def load_models(visits_model_path, infections_model_path):
   visits_model = np.load(visits_model_path, allow_pickle=True).item()
   infections_model = np.load(infections_model_path, allow_pickle=True).item()
   return visits_model, infections_model


def predict(visits_model, infections_model, input_features):
   visits_prediction = visits_model.predict(input_features)
   infections_prediction = infections_model.predict(input_features)
   return visits_prediction, infections_prediction

def regression_model(latitude_example: float, longitude_example: float, days_ahead: int):

   visits_model, infections_model = load_models(VISITS_PIPELINE, INFECTIONS_PIPELINE)

   prediction_date = datetime.now() + timedelta(days=days_ahead)

   input_data = np.array([[latitude_example, longitude_example, prediction_date.weekday(), prediction_date.month]])

   predicted_visits = visits_model.predict(input_data)
   predicted_infections = infections_model.predict(input_data)

   return np.round(predicted_visits[0]).astype(int), np.round(predicted_infections[0]).astype(int)

