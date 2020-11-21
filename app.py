import requests
import os
import urllib.parse
import json

from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory, url_for, request, redirect, session
from airtable import Airtable
from datetime import datetime, timedelta

load_dotenv(dotenv_path="./config.py")

# set the "static" directory as the static folder
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.getenv("APP_SECRET")

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("BASE_ID")

def verify(user, pw):
    airtable = Airtable(BASE_ID, 'Authentication', API_KEY)
    user_data = airtable.search("ID", user)

    if user_data:
        user_password = user_data[0]["fields"]["Password"]
        if user_password == pw:
            return user_data[0]["fields"]["ID"]
    
    return False

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    user_id = session.get("user", None)
    if user_id:
        return render_template("index.html")
    
    return redirect(url_for("login"))

@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        user = request.form.get("id")
        pw = request.form.get("pw")

        uid = verify(user, pw)

        if uid:
            session["user"] = uid
            return redirect(url_for("index"))

        return render_template("login.html")
    
    user_id = session.get("user", None)
    if user_id:
        return redirect(url_for("index"))
    
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user", None)
    return(redirect(url_for("login")))

#function to create html anchors
def htmlanchor(link):
    return "<a href='" + link + "' target='_blank'>" + link + "</a>"

@app.route('/schedules', methods=['GET', 'POST'])
def schedules():
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    BASE_ID = "appqzHMiklMrdGU3D"
    ppantID = 1900
    
    #get data of ppant
    stagger=0
    timezoneID=''
    familyID=''
    cabinID=''
    createID=''
    for page in Airtable(BASE_ID, 'Participant', API_KEY).get_iter(formula=f"{{ID}}={ppantID}"):
        for record in page:
            stagger = record['fields']['Stagger'][0]
            timezoneID = record['fields']['TimeZone'][0]
            familyID = record['fields']['Family'][0]
            cabinID = record['fields']['Cabin'][0]
            createID = record['fields']['Create Room'][0]


    #get timezone info
    timezoneInfo = Airtable(BASE_ID,'TimeZone', API_KEY).get(timezoneID)
    timezone = timezoneInfo['fields']['TimeZone']
    timezoneOffset = timezoneInfo['fields']['GMT Offset']
    # print(timezone)
    # print(timezoneOffset)

    #get family link
    familyLink = Airtable(BASE_ID,'Family', API_KEY).get(familyID)['fields']['Zoom Link']
    # print(familyLink)

    #get cabin link
    cabinLink = Airtable(BASE_ID,'Cabin', API_KEY).get(cabinID)['fields']['Zoom Link']
    # print(cabinLink)

    #get create link
    createLink = Airtable(BASE_ID,'Create', API_KEY).get(createID)['fields']['Zoom Link']
    # print(createLink)
      
    #get sch data using ppant stagger
    schInfo = Airtable(BASE_ID, 'Schedule', API_KEY).get_all(formula=f"{{Stagger}}={stagger}",sort=['Day', '-Order']) # -order because they're put in backwards in the for loop

    #list that will store organize the schData objects for the table
    schArr = []

    #camp start date for stagger and duration tracker
    startdate = datetime(year=2020, month=12, day=26, hour=10, minute=30)
    durTracker = datetime(year=2020, month=12, day=26, hour=0, minute=0)
    if stagger==2:
        startdate = datetime(year=2020, month=12, day=26, hour=13, minute=30)

    #day tracker 
    day = 0
    for record in schInfo:
        schData = {}

        #DateTime Ranges
        duration = schInfo[len(schArr)]['fields']['Duration']

        if(day != schInfo[len(schArr)]['fields']['Day']):
            day = schInfo[len(schArr)]['fields']['Day']
            durTracker = startdate + timedelta(days=(day-1), hours=timezoneOffset)

        schData[1] = durTracker
        durTracker = durTracker + timedelta(minutes=duration)
        schData[0] = datetime.strftime(schData[1], "%b %-d")
        schData[1] = datetime.strftime(schData[1], "%H:%M") + ' - ' + datetime.strftime(durTracker, "%H:%M") + ' ' + timezone

        #Activity
        schData[2] = schInfo[len(schArr)]['fields']['ActivityType']

        #Zoom Link
        if 'Cabin' in schData[2]:
            schData[3] = htmlanchor(cabinLink)
        elif 'Transition' in schData[2]:
            schData[3] = 'Transition'
        elif 'Gather' in schData[2]:
            schData[3] = htmlanchor(familyLink)
        elif 'Break' in schData[2]:
            schData[3] = 'Break'
        elif 'Create' in schData[2]:
            schData[3] = htmlanchor(createLink)
        elif 'Explore' in schData[2]:
            schData[3] = htmlanchor(familyLink)
        else:
            schData[3]=schData[2]
        
        schArr.append(schData)

    #get camp day #, default to 1
    campday = (datetime.utcnow().day % 25) if 0<(datetime.utcnow().day % 26)<7 else 1

    return render_template('schedules.html', data=schArr, campday=campday)

@app.errorhandler(401)
def FUN_401(error):
    return render_template("401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("413.html"), 413

if __name__ == "__main__":
    # get_some_data()
    app.run(debug=True, host="localhost")
