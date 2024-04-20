import pandas as pd
import matplotlib.pyplot as plt
from src.app import create_patrol_app
from sqlalchemy.sql import text
from src.database.db import db

app = create_patrol_app()

def fetchVaccinationRecord():
    sql = text('SELECT DISTINCT(user_id) FROM vaccination_history')
    result = db.session.execute(sql)
    data = result.fetchall()
    return len(data)
    # print(result)

def fetchInfectionRecord():
    sql = text('SELECT DISTINCT(user_id) FROM infection_history')
    result = db.session.execute(sql)
    data = result.fetchall()
    return len(data)

if __name__ == '__main__':
    with app.app_context():
        vaccinatedCount = fetchVaccinationRecord()
        infectedCount   = fetchInfectionRecord()
        print("Total No. of vaccinated people are" ,vaccinatedCount)
        print("Total No. of infected people are", infectedCount)
