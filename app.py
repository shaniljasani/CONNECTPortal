import requests
import os
import urllib.parse

from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
load_dotenv(dotenv_path="./config.py")

# set the "static" directory as the static folder
app = Flask(__name__, static_url_path='/static')

API_KEY=os.getenv("AIRTABLE_API_KEY")

def get_some_data():
    BASE_ID = "appm9g9Ewv87tg8al" # Add base id of AirTable application
    TABLE_NAME = "Feedback Session"

    response = requests.get('https://api.airtable.com/v0/' + BASE_ID + '/' + urllib.parse.quote(TABLE_NAME), headers={'Authorization': 'Bearer ' + API_KEY})
    data = response.json()

    print(data)

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def hello():
    return render_template("index.html")

if __name__ == "__main__":
    get_some_data()
    # app.run(debug=True, host="localhost")