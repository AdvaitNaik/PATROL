import hashlib
from src.database.db import db  # Adjust the import as per your project structure
from src.database.model import User  # Ensure User class is imported correctly
from faker import Faker
import numpy as np
import random
from src.app import create_patrol_app

# Initialize Faker
fake = Faker()
app = create_patrol_app()

# Constants for Los Angeles coordinates
# LA_LAT = 34.0522
# LA_LNG = -118.2437
# COORD_VARIATION = 0.1  # Maximum variation degree

# Function to generate nearby coordinates
# def generate_nearby_coords(lat, lng, variation=COORD_VARIATION):
#     return (lat + np.random.uniform(-variation, variation),
#             lng + np.random.uniform(-variation, variation))

def create_uuid_hash(uuid: str):
    sha1 = hashlib.sha1()
    sha1.update(uuid.encode('utf-8'))
    # hashed_uuid = sha1.hexdigest()
    return sha1.hexdigest()

# Function to create user data with LA nearby coords and add to database
def add_users(num_users):
    users = []
    for _ in range(num_users):
        uuid = fake.uuid4()  # Generates a new UUID
        # lat, lng = generate_nearby_coords(LA_LAT, LA_LNG)
        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            uuid=uuid,
            uuid_hash=create_uuid_hash(uuid),  # Hash the generated UUID
            role_name='GEN'  # Assuming 'GEN' is a valid role in your User model
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()  # Commit at the end of the function
    return users

if __name__ == '__main__':
    with app.app_context():
        num_users = 10  # Number of users to generate
        add_users(num_users)
