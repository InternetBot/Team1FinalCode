#!/bin/bash

# Wait for the database to be ready
echo "Waiting for database to be ready..."
python -c "
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(
                dbname='immun_db',
                user='postgres',
                password='postgres',
                host='db',
                port='5432'
            )
            conn.close()
            print('Database is ready!')
            return
        except OperationalError:
            print('Waiting for database...')
            time.sleep(1)

wait_for_db()
"

# Initialize the database and create default admin account
python -c "from app.init_db import init_db; init_db()"

# Start the Flask application
flask run --host=0.0.0.0 