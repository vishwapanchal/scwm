import mysql.connector
from mysql.connector import Error
import json

# Connection Config for AWS RDS MySQL
DB_CONFIG = {
    "host": "aws.c07cik8ugpex.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "vishwarp",
    "port": 3306
}

TARGET_DB = "aws"

def init_db():
    conn = None
    try:
        print(f"🔌 Connecting to AWS RDS MySQL ({DB_CONFIG['host']})...")
        # Connect without DB first to ensure it exists
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Create Database if not exists
        print(f"🔨 Check/Create Database: {TARGET_DB}")
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {TARGET_DB}")
        cur.execute(f"USE {TARGET_DB}")

        # --- DEFINE TABLES ---
        
        # 1. Scans / Waste Logs
        # Note: MySQL uses AUTO_INCREMENT instead of SERIAL
        print("🔨 Creating table: scans...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                waste_type VARCHAR(255) NOT NULL,
                confidence FLOAT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                latitude FLOAT,
                longitude FLOAT,
                image_url TEXT,
                gemini_advice TEXT
            );
        """)

        # 2. Recycling Centers
        # Note: MySQL uses JSON type for arrays
        print("🔨 Creating table: recycling_centers...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recycling_centers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address TEXT NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                accepted_materials JSON, 
                contact_info VARCHAR(255),
                website VARCHAR(255)
            );
        """)

        # 3. Waste Categories
        print("🔨 Creating table: waste_categories...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS waste_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                general_recovery_protocol TEXT,
                environmental_impact TEXT
            );
        """)

        conn.commit()
        
        # --- SEED DATA ---
        
        # Check if centers exist
        cur.execute("SELECT COUNT(*) FROM recycling_centers")
        count = cur.fetchone()[0]
        
        if count == 0:
            print("🌱 Seeding sample recycling center data...")
            # Note: In MySQL, we pass JSON as a string
            sql = """INSERT INTO recycling_centers 
                     (name, address, latitude, longitude, accepted_materials, contact_info) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            
            val = [
                ('Bengaluru Construction Recyclers', '123 Industrial Way', 12.9716, 77.5946, json.dumps(['concrete', 'bricks']), '080-12345678'),
                ('EcoMetal Solutions', '45 Green Zone', 12.9352, 77.6245, json.dumps(['metal', 'copper']), '080-87654321')
            ]
            cur.executemany(sql, val)
            conn.commit()

        cur.close()
        print("✅ Database Schema initialized successfully on AWS RDS MySQL!")

    except mysql.connector.Error as e:
        print("\n❌ CONNECTION ERROR:")
        print(f"Error Code: {e.errno}")
        print(f"Message: {e.msg}")
        print("Tips: Check AWS Security Group (Port 3306) and Public Accessibility.")
    except Exception as e:
        print(f"\n❌ GENERIC ERROR: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    init_db()
