import pandas as pd
import sqlite3
import os

# Putanja do baze
db_path = 'database.db'

# Provjera postoji li baza te izrada tablice
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS travel_details (
            Trip_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Destination_city TEXT,
            Destination_country TEXT,
            Start_date DATE,
            End_date DATE,
            Duration_days INTEGER,
            Traveler_name TEXT,
            Traveler_age INTEGER,
            Traveler_gender TEXT,
            City_of_residence TEXT,
            Traveler_nationality TEXT,
            Accommodation_type TEXT,
            Accommodation_cost INTEGER,
            Transportation_type TEXT,
            Transportation_cost INTEGER
        )
    ''')

    df = pd.read_csv('Travel_details.csv', delimiter=',', encoding='latin-1')
    df.to_sql('travel_details', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
