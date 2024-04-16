from src.database.db import db  # Adjust the import as per your project structure
from src.database.model import User  # Ensure User class is imported correctly
from faker import Faker
import numpy as np
import random

# Initialize Faker
fake = Faker()

# Constants for Los Angeles coordinates
LA_LAT = 34.0522
LA_LNG = -118.2437
COORD_VARIATION = 0.1  # Maximum variation degree

# Function to generate nearby coordinates
def generate_nearby_coords(lat, lng, variation=COORD_VARIATION):
    return (lat + np.random.uniform(-variation, variation),
            lng + np.random.uniform(-variation, variation))

# Function to create user data with LA nearby coords and add to database
def add_users(num_users):
    users = []
    for _ in range(num_users):
        lat, lng = generate_nearby_coords(LA_LAT, LA_LNG)
        user = User(
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            country_code='+1',
            email=fake.email(),
            address=fake.street_address(),
            city='Los Angeles',
            state='CA',
            country='USA',
            zip_code=fake.zipcode_in_state(state_abbr='CA'),
            latitude=lat,
            longitude=lng
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()  # Commit at the end of the function
    return users

# Generate data
num_users = 1000  # Number of users to generate
add_users(num_users)
