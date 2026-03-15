import requests
import smtplib
import json
import os
from email.mime.text import MIMEText

API_KEY = "YOUR_SERPAPI_KEY"  # ← replace

EMAIL_FROM = "j.caseygavin@gmail.com"  # ← replace
EMAIL_PASSWORD = "your_app_password"  # ← replace
EMAIL_TO = "jgavin269@hotmail.com"

departures = ["TYS"]
arrivals = ["ORD","MDW"]

OUT_DATE = "2026-06-05"
RET_DATE = "2026-06-07"

price_file = "lowest_price.json"

# Load previous lowest price
if os.path.exists(price_file):
    with open(price_file,"r") as f:
        stored_price = json.load(f)["price"]
else:
    stored_price = 9999

lowest_today = 9999
best_flight = ""

for dep in departures:
    for arr in arrivals:

        params = {
            "engine":"google_flights",
            "departure_id":dep,
            "arrival_id":arr,
            "outbound_date":OUT_DATE,
            "return_date":RET_DATE,
            "adults":1,
            "children":1,
            "stops":1,
            "currency":"USD",
            "api_key":API_KEY
        }

        r = requests.get("https://serpapi.com/search.json",params=params)
        data = r.json()

        flights = data.get("best_flights",[])

        if flights:
            price = flights[0]["price"]
            airline = flights[0]["flights"][0]["airline"]
            depart_time = flights[0]["flights"][0]["departure_airport"]["time"]
            arrive_time = flights[0]["flights"][0]["arrival_airport"]["time"]

            if price < lowest_today:
                lowest_today = price
                best_flight = f"{dep} → {arr} | {airline} | ${price} | {depart_time}-{arrive_time}"

# Send email if new lowest
if lowest_today < stored_price:
    body = f"New cheapest Chicago flight found!\n\n{best_flight}"

    msg = MIMEText(body)
    msg["Subject"] = "✈️ New Cheapest Chicago Flight"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login(EMAIL_FROM,EMAIL_PASSWORD)
    server.sendmail(EMAIL_FROM,EMAIL_TO,msg.as_string())
    server.quit()

    with open(price_file,"w") as f:
        json.dump({"price":lowest_today},f)
