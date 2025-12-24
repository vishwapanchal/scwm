# -*- coding: utf-8 -*-
import mysql.connector
import os
import csv
import io
from dotenv import load_dotenv

load_dotenv()

# Raw data provided by the user
csv_raw = """name,address,latitude,longitude,contact_info
BBMP Construction Waste Unit,Chikkajala Bengaluru,12.9716,77.5946,080-22975518
BBMP Construction Waste Unit,Kannur Bengaluru,12.9716,77.5946,080-22975518
BBMP Construction Waste Unit,Channasandra Bengaluru,12.9716,77.5946,080-22975518
Rock Crystals C&D Recycler,Bengaluru,12.9716,77.5946,080-22975518
Picson Construction Equipments Pvt. Ltd.,Bengaluru,12.9716,77.5946,080-22975518
Let's Recycle,Bengaluru,12.9716,77.5946,080-22975518
Attero Recycling Pvt. Ltd.,Bengaluru,12.9716,77.5946,080-22975518
APM Enterprises,Bengaluru,12.9716,77.5946,+917942619671
H.K. Contractor,Bengaluru,12.9716,77.5946,080-22975518
M S Traders,Bengaluru,12.9716,77.5946,9900123456
K P P Alloys,Bengaluru,12.9716,77.5946,9900123456
Sri Radhakrishna Enterprises,Bengaluru,12.9716,77.5946,9900123456
A S Enterprises (Building Demolishers),Bengaluru,12.9716,77.5946,9900123456
A J Enterprises,Bengaluru,12.9716,77.5946,9900123456
Siddarth Industrial Suppliers,Bengaluru,12.9716,77.5946,9900123456
Amk Scrap Traders,Bengaluru,12.9716,77.5946,9900123456
M M Royal Furniture and Scrap Buyers,Bengaluru,12.9716,77.5946,9900123456
Sri Sai Polymer,Bengaluru,12.9716,77.5946,9900123456
RN India Enterprises,Bengaluru,12.9716,77.5946,+917942541699
TT Recycling Management India Pvt. Ltd.,Bengaluru,12.9716,77.5946,amit.dubey@ttri.co.in
Green India E-Waste & Recycling OPC Pvt. Ltd.,Bengaluru,12.9716,77.5946,9900123456
Victoria Swachha Eco Solutions,Bengaluru,12.9716,77.5946,7411739900
Synergy Waste Management Pvt. Ltd.,Bengaluru,12.9716,77.5946,9900123456
A2Z Group,Bengaluru,12.9716,77.5946,9900123456
Banyan Nation,Bengaluru,12.9716,77.5946,9900123456
APChemi,Bengaluru,12.9716,77.5946,9900123456
Vermigold Ecotech,Bengaluru,12.9716,77.5946,9900123456
Tarai Projects Pvt. Ltd.,Bengaluru,12.9716,77.5946,9900123456
ASK Steel,Bengaluru,12.9716,77.5946,9900123456
Raj Enterprises,Bengaluru,12.9716,77.5946,9900123456
Antony Waste Handling Cell Ltd.,Bengaluru,12.9716,77.5946,9900123456
EverEnviro Burari,Bengaluru,12.9716,77.5946,9900123456
North Delhi Municipal Corporation C&D Plant,Bengaluru,12.9716,77.5946,9900123456
Bakkarwala C&D Waste Plant,Bengaluru,12.9716,77.5946,9900123456
Ranikhera C&D Waste Plant,Bengaluru,12.9716,77.5946,9900123456
Shastri Park C&D Waste Plant,Bengaluru,12.9716,77.5946,9900123456
UTTAR DILLI C&D Waste Recycling Pvt. Ltd.,Bengaluru,12.9716,77.5946,9900123456
Scrapwala Building/Construction Waste Services,Bengaluru,12.9716,77.5946,9900123456
Mumbai C&D Waste Processing Plant,Bengaluru,12.9716,77.5946,9900123456
Daighar C&D Waste Plant,Bengaluru,12.9716,77.5946,9900123456
Deonar C&D Waste Plant,Bengaluru,12.9716,77.5946,9900123456
Shah Recycling,Bengaluru,12.9716,77.5946,9900123456
Antony Waste & CFlo C&D Plant,Bengaluru,12.9716,77.5946,9900123456
Mumbai C&D Recycling Plant,Bengaluru,12.9716,77.5946,9900123456
Sky-Tech Scrap Dealer,Bengaluru,12.9716,77.5946,9900123456
Greater Chennai Corporation C&D Plant,Bengaluru,12.9716,77.5946,9900123456"""

def run_seed():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        cursor = conn.cursor()
        
        # 1. Clean data: Remove potential duplicate names and empty lines
        f = io.StringIO(csv_raw)
        reader = csv.DictReader(f)
        cleaned_list = []
        for row in reader:
            if row['name'] and row['latitude']:
                cleaned_list.append((
                    row['name'],
                    row['address'],
                    float(row['latitude']),
                    float(row['longitude']),
                    row['contact_info']
                ))

        # 2. Clear old table
        print("Ì∑π Clearing existing data...")
        cursor.execute("TRUNCATE TABLE recycling_centers")
        
        # 3. Insert new Bengaluru data
        query = "INSERT INTO recycling_centers (name, address, latitude, longitude, contact_info) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(query, cleaned_list)
        conn.commit()
        
        print(f"‚úÖ Successfully pushed {len(cleaned_list)} centers to Bengaluru map!")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"‚ùå Error during seeding: {e}")

if __name__ == "__main__":
    run_seed()
