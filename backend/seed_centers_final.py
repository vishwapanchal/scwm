# -*- coding: utf-8 -*-
import mysql.connector
import os
import csv
import io
from dotenv import load_dotenv

load_dotenv()

# Raw data string cleaned of duplicates and extraneous URLs
csv_raw = """name,address,latitude,longitude,contact_info
M/s Indo Enviro Integrated Solutions Limited,Shastri Park Delhi,28.7198,77.2152,+91 9566233928
M/s Indo Enviro Integrated Solutions Limited,Mundka Delhi,28.6965,77.0645,+91 9566233928
M/s Indo Enviro Integrated Solutions Limited,Rohini Delhi,28.7375,77.1139,+91 9566233928
M/s Rise Eleven Delhi Waste Management Co.,Bakkarwala Village Delhi,28.6592,77.1184,+91 9810883930
M/s Indo Enviro Integrated Solutions Limited,Mundka Site Delhi,28.6965,77.0645,+91 9566233928
Picson Construction Equipments Pvt. Ltd.,Delhi,28.6139,77.2090,011-41002200
UTTAR DILLI C&D Waste Recycling Pvt. Ltd.,Okhla Phase-3 Delhi,28.5355,77.2962,011-26923300
Scrapwala Construction Waste Services,New Delhi,28.6139,77.2090,011-41002200
Mumbai C&D Waste Processing Plant,Dahisar Mumbai,19.2408,72.8718,022-28873000
Daighar C&D Waste Plant,Daighar Mumbai,19.2000,72.9500,022-28873000
Deonar C&D Waste Plant,Deonar Mumbai,19.0667,72.8833,022-28873000
Shah Recycling,Mumbai,19.0760,72.8777,022-28873000
Picson Construction Equipments Pvt. Ltd.,Mumbai,19.0760,72.8777,022-28873000
Antony Waste & CFlo C&D Plant,Mumbai,19.0760,72.8777,022-28873000
Mumbai C&D Recycling Plant,Wadala Mumbai,19.0400,72.8500,022-28873000
Sky-Tech Scrap Dealer,Mumbai,19.0760,72.8777,+91-7021162566
BBMP Construction Waste Unit,Chikkajala Bengaluru,12.9716,77.5946,080-22975518
BBMP Construction Waste Unit,Kannur Bengaluru,12.9716,77.5946,080-22975518
BBMP Construction Waste Unit,Channasandra Bengaluru,12.9716,77.5946,080-22975518
Rock Crystals C&D Recycler,Bengaluru,12.9716,77.5946,080-22975518
Picson Construction Equipments Pvt. Ltd.,Bengaluru,12.9716,77.5946,080-22975518
Greater Chennai Corporation C&D Plant,Kodungaiyur Chennai,13.0827,80.2707,044-25610000
Greater Chennai Corporation C&D Plant,Perungudi Chennai,12.9716,80.2342,044-25610000
Greater Chennai Corporation C&D Plant,Manali Chennai,13.1222,80.2500,044-25610000
Picson Construction Equipments Pvt. Ltd.,Chennai,13.0827,80.2707,044-25610000
GHMC C&D Waste Recycling Plant,Jeedimetla Hyderabad,17.4507,78.4195,040-23111311
GHMC C&D Waste Recycling Plant,Fathullaguda Hyderabad,17.4507,78.4195,040-23111311
Arcler AFR Plant at Ramky,Hyderabad,17.4507,78.4195,040-23111311
Picson Construction Equipments Pvt. Ltd.,Hyderabad,17.4507,78.4195,040-23111311
SSN Innovative Infra LLP C&D Plant,Pune,18.6167,73.8000,020-25526000
Shah Recycling,Pune,18.5204,73.8567,020-25526000
Picson Construction Equipments Pvt. Ltd.,Pune,18.5204,73.8567,020-25526000
KMC C&D Waste Recycling Plant,Kolkata,22.5726,88.3639,033-22861000
Re Sustainability C&D Plant,Kolkata,22.5726,88.3639,033-22861000
Convotech Engineering C&D Plant,Kolkata,22.5726,88.3639,033-22861000
Picson Construction Equipments Pvt. Ltd.,Kolkata,22.5726,88.3639,033-22861000
Ahmedabad Municipal Corporation MRF,Ahmedabad,23.0225,72.5714,079-25506000
Vaslly Recycling Pvt. Ltd.,Ahmedabad,23.0225,72.5714,079-25506000
Picson Construction Equipments Pvt. Ltd.,Ahmedabad,23.0225,72.5714,079-25506000
Clean Surat Centre,Surat,21.1702,72.8311,0261-2570500
Attero Recycling,Bangalore,12.9716,77.5946,080-22975518
Banyan Nation,Hyderabad,17.4507,78.4195,040-23111311
APChemi,Chennai,13.0827,80.2707,044-25610000
Vermigold Ecotech,Mumbai,19.0760,72.8777,022-28873000
Synergy Waste Management,Delhi,28.6139,77.2090,011-41002200
A2Z Group,Delhi,28.6139,77.2090,011-41002200
Let's Recycle,Bengaluru,12.9716,77.5946,080-22975518
Green India E-Waste,Thane,19.2183,72.9781,022-28873000
Tarai Projects,Pune,18.6167,73.8000,020-25526000
Victoria Eco Solutions,Krishnagiri,12.5139,78.3517,7411739900
Sri Poly Tech,Chennai,13.0827,80.2707,9444062220
Sri Sai Polymer,Chennai,13.0827,80.2707,9941640037
RN India Enterprises,Nagpur,21.1458,79.0882,917942541699
APM Enterprises,Bengaluru,12.9716,77.5946,917942619671
H.K. Contractor,Bengaluru,12.9716,77.5946,080-22975518
EverEnviro Burari,Delhi,28.7867,77.1597,1800-11-6767
Ranikhera C&D Plant,Delhi,28.7565,77.2052,011-27305100
Shastri Park Plant,Delhi,28.6985,77.2565,011-27305100
Sanjari Recycling,Bhiwandi,19.2985,73.1060,8262033359
S Alam Scrap Yard,Garhwa,23.6120,84.6337,7488326145
Sattva Global,Hyderabad,17.4507,78.4195,09701231075
Indian Scrap Traders,Bangalore,12.9716,77.5946,9886576172
Earth Sense Recycle,Chennai,13.0827,80.2707,044-42014765"""

def seed():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        cursor = conn.cursor()
        
        # Data cleaning: Remove duplicates by name
        f = io.StringIO(csv_raw)
        reader = csv.DictReader(f)
        seen_names = set()
        cleaned_data = []
        
        for row in reader:
            if row['name'] not in seen_names:
                cleaned_data.append((
                    row['name'],
                    row['address'],
                    float(row['latitude']),
                    float(row['longitude']),
                    row['contact_info']
                ))
                seen_names.add(row['name'])

        # Refresh table
        cursor.execute("TRUNCATE TABLE recycling_centers")
        
        query = "INSERT INTO recycling_centers (name, address, latitude, longitude, contact_info) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(query, cleaned_data)
        conn.commit()
        
        print(f"✅ Cleaned and Pushed {len(cleaned_data)} unique locations!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    seed()
