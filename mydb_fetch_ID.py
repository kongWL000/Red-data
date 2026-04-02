import mysql.connector
import requests
import os

# --- Step 0: Set up file path (not used now, but retained in case you re-enable later) ---
script_dir = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(script_dir, "last_id.txt")

# --- Step 1: Fetch all data from AWS RDS ---
config = {
    "host": "aurora-trans-ro.prod.fibonacci.internal",
    "port": 3306,
    "user": "insight_services_ro",
    "password": "4rtt9rebibretwq256d9ytr33e76yte",
    "ssl_ca": "C:\\rds-ca.pem"
}

query = """
SELECT
  company_id,
  crm_account_id,
  company_name,
  account_name,
  opportunity_name,
  report_name,
  report_dt
FROM insights_services.insight_reports_with_clicks

UNION

SELECT
  company_id,
  crm_account_id,
  company_name,
  account_name,
  opportunity_name,
  report_name,
  report_dt
FROM insights_services.insight_reports_not_clicked

ORDER BY company_id ASC
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

# --- Step 2: Prepare data to send ---
data_to_send = []

for row in rows:
    data_to_send.append([
        row["company_id"],
        row["crm_account_id"],
        row["company_name"],
        row["account_name"],
        row["opportunity_name"],
        row["report_name"],
        str(row["report_dt"])
    ])

# --- Step 3: Send to Google Sheets ---
url = 'https://script.google.com/macros/s/AKfycbww2FA2Rdxjp9pQr8k-6YFuG9ZJ2NhhN_llzEQe7lY69Stj2egKY7tV9Y2u7GYwRTgL/exec'

try:
    if data_to_send:
        response = requests.post(url, json=data_to_send)
        print("Google Sheets response:", response.text)
    else:
        print("No data to send.")
except Exception as e:
    print(f"Error while sending to Google Sheets: {e}")
