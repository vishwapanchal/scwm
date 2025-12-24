import os
import mysql.connector
import json
from dotenv import load_dotenv

load_dotenv()

# Connect to the 'aws' Database
try:
    print(f"🔌 Connecting to database '{os.getenv('DB_NAME')}'...")
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"), # This should be 'aws' now
        port=int(os.getenv("DB_PORT"))
    )
    cursor = conn.cursor()

    # --- 1. Create Scans Table ---
    print("🔨 Creating table: scans...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            waste_type VARCHAR(255) NOT NULL,
            confidence FLOAT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            gemini_advice TEXT
        );
    """)

    # --- 2. Create Recycling Centers Table ---
    print("🔨 Creating table: recycling_centers...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recycling_centers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address TEXT NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            contact_info VARCHAR(255)
        );
    """)

    # --- 3. Seed Recycling Centers (If empty) ---
    cursor.execute("SELECT COUNT(*) FROM recycling_centers")
    if cursor.fetchone()[0] == 0:
        print("🌱 Seeding recycling centers map data...")
        sql = "INSERT INTO recycling_centers (name, address, latitude, longitude, contact_info) VALUES (%s, %s, %s, %s, %s)"
        val = [
            ('Bengaluru Construction Recyclers', '123 Industrial Way', 12.9716, 77.5946, '080-12345678'),
            ('EcoMetal Solutions', '45 Green Zone', 12.9352, 77.6245, '080-87654321'),
            ('North Bangalore Waste Mgmt', 'Hebbal Industrial Area', 13.0359, 77.5971, '080-55555555')
        ]
        cursor.executemany(sql, val)
        conn.commit()

    print("✅ All Tables Created & Data Seeded Successfully!")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")