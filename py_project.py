import requests
import sqlite3
import json
import time
from datetime import date


db = sqlite3.connect('test.db')
terminal = db.cursor()


terminal.execute('''
CREATE TABLE IF NOT EXISTS exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    currency TEXT,
    unit INTEGER,
    buy_rate REAL,
    sell_rate REAL,
    rate_date TEXT
)
''')

terminal.execute('''
CREATE TABLE IF NOT EXISTS viber_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

db.commit()


def send_message_to_viber(message):

    token = "5726a91993b094bf-68bf2589b9b1571e-b238a9f87e9d5824"
    user_token = "o8qjkhvsdO0Z1ibTipUW4Q=="
    viber_url = "https://chatapi.viber.com/pa/post"


    data = {
            "auth_token": token,
            "from": user_token,
            "type": "text",
            "text": message
        }

    r = requests.post(
            url=viber_url,
            data=json.dumps(data)
        )

    if r.status_code == 200:
        result = r.json()

        if result['status'] == 0:

            print("Message sent successfully")

            terminal.execute('''
                INSERT INTO viber_messages (message)
                VALUES (?)
                ''', (message,))

            db.commit()

        else:
            print("Viber error:", result)

    else:
        print("Request failed:", r.status_code, r.text)
        

def get_data():

    today = date.today().strftime("%Y-%m-%d")

    data_url = "https://www.nrb.org.np/api/forex/v1/rates"

    params = {
        "page": 1,
        "per_page": 100,
        "from": today,
        "to": today
    }

    r = requests.get(url=data_url, params=params)

    if r.status_code == 200:

        response = r.json()

        result = response["data"]["payload"]

        if not result:
            print("No exchange rates available for this date.")
            return

        rates = result[0]["rates"]

        message = f"Nepal Exchange Rates\nDate: {today}\n\n"

        for item in rates:

            currency = item["currency"]["iso3"]
            unit = item["currency"]["unit"]
            buy = item["buy"]
            sell = item["sell"]

           
            terminal.execute('''
            INSERT INTO exchange_rates
            (currency, unit, buy_rate, sell_rate, rate_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (currency, unit, buy, sell, today))

            
            message += (
                f"{currency} (Unit: {unit})\n"
                f"Buy: {buy} | Sell: {sell}\n\n"
            )

        db.commit()

        print("Exchange rates stored in database")

    
        send_message_to_viber(message)

    else:
        print("API request failed:", r.status_code)


get_data()

db.close()