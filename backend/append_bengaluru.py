# -*- coding: utf-8 -*-
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def remove_duplicates():
    try:
        print(f"🔌 Connecting to AWS RDS to clean data...")
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        cursor = conn.cursor()

        # SQL Logic: Identify duplicates by name and address, keep the one with the lowest ID
        # 
        delete_query = """
        DELETE t1 FROM recycling_centers t1
        INNER JOIN recycling_centers t2 
        WHERE 
            t1.id > t2.id AND 
            t1.name = t2.name AND 
            t1.address = t2.address;
        """
        
        cursor.execute(delete_query)
        rows_affected = cursor.rowcount
        conn.commit()

        print(f"✨ Success! Removed {rows_affected} duplicate entries.")
        
        # Verify current count
        cursor.execute("SELECT COUNT(*) FROM recycling_centers")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total unique centers remaining: {total_count}")

        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Deduplication Failed: {e}")

if __name__ == "__main__":
    remove_duplicates()