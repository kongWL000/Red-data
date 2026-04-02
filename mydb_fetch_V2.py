import mysql.connector
import requests
import os

# --- Step 0: Load last ID from file ---
script_dir = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(script_dir, "last_id.txt")

default_start_id = 199824

if os.path.exists(last_id_file):
    with open(last_id_file, "r") as f:
        last_id = int(f.read().strip())
else:
    last_id = default_start_id
    

# --- Step 1: Fetch data from AWS RDS ---
config = {
    "host": "aurora-trans-ro.prod.fibonacci.internal",
    "port": 3306,
    "user": "insight_services_ro",
    "password": "4rtt9rebibretwq256d9ytr33e76yte",
    "ssl_ca": "C:\\rds-ca.pem"
}

query = f"""
SELECT
  id,
  received_ts,
  CAST(document_url AS CHAR(2048)) AS document_url,
  report_dt,
  CAST(report_name AS CHAR(255)) AS report_name,
  slide_nbr,
  company_id,
  crm_instance_id,
  crm_account_id,
  is_likely_bot_ind,
  aws_insert_ts
FROM insights_services.is_custom_report_clicks
WHERE id > {last_id}
ORDER BY id ASC
"""

rows = []

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
except mysql.connector.Error as err:
    print(f"MySQL Error: {err}")

# --- Step 2: Prepare data ---
data_to_send = []
max_id = last_id

for row in rows:
    data_to_send.append([
        row["id"],
        str(row["received_ts"]),
        row["document_url"],
        str(row["report_dt"]),
        row["report_name"],
        row["slide_nbr"],
        row["company_id"],
        row["crm_instance_id"],
        row["crm_account_id"],
        row["is_likely_bot_ind"],
        str(row["aws_insert_ts"])
    ])
    if row["id"] > max_id:
        max_id = row["id"]

# --- Step 3: Send to Google Sheets ---
url = 'https://script.google.com/macros/s/AKfycbzQsXT5wXz2ScUmXD_jyshOW_f-5IpFzDeQ9-gWFa-gGg10yKZ-E18G-A9LNNdt9rhZ/exec'

try:
    if data_to_send:
        response = requests.post(url, json=data_to_send)
        print("Google Sheets response:", response.text)

        # Save new last ID to file only if POST is successful
        if response.status_code == 200:
            with open(last_id_file, "w") as f:
                f.write(str(max_id))
        else:
            print("Data sent but did not receive a 200 response. Last ID not updated.")
    else:
        print("No new data to send.")
except Exception as e:
    print(f"Error while sending to Google Sheets: {e}")
