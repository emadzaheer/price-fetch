import sqlite3
import time
import requests
from flask import Flask, render_template

# Coinbase Pro API endpoints for CUDOS and USDC
CUDOS_URL = 'https://api.pro.coinbase.com/products/CUDOS-USD/ticker'
USDC_URL = 'https://api.pro.coinbase.com/products/USDC-USD/ticker'

# Create a Flask application
app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect('prices.db')
c = conn.cursor()

# Create a table to store the prices
c.execute('''CREATE TABLE IF NOT EXISTS prices
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              timestamp INTEGER,
              cudos_price REAL,
              usdc_price REAL)''')
conn.commit()

# Function to fetch the current prices and insert into the database
def update_prices():
    # Fetch the CUDOS and USDC prices from Coinbase Pro API
    cudos_response = requests.get(CUDOS_URL).json()
    usdc_response = requests.get(USDC_URL).json()
    cudos_price = float(cudos_response['price'])
    usdc_price = float(usdc_response['price'])

    # Insert the prices into the database
    timestamp = int(time.time())
    c.execute('INSERT INTO prices (timestamp, cudos_price, usdc_price) VALUES (?, ?, ?)', (timestamp, cudos_price, usdc_price))
    conn.commit()

# Route to display the latest prices
@app.route('/')
def index():
    c.execute('SELECT * FROM prices ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    if row:
        timestamp, cudos_price, usdc_price = row[1], row[2], row[3]
        return render_template('index.html', timestamp=timestamp, cudos_price=cudos_price, usdc_price=usdc_price)
    else:
        return 'No data available'

# Run the update_prices function every 5 seconds
while True:
    update_prices()
    time.sleep(5)

# Close the database connection
conn.close()
