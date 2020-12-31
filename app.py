import requests
import os
import urllib.parse
import json
import pytz
import git

from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory, url_for, request, redirect, session
from airtable import Airtable
from datetime import datetime, timedelta, tzinfo

utc = pytz.utc
load_dotenv(dotenv_path="./config.py")

# set the "static" directory as the static folder
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.getenv("APP_SECRET")

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("BASE_ID")
G_ANALYTICS = os.getenv("G_ANALYTICS")

@app.context_processor
def inject_analytics():
    return dict(analytics_id=G_ANALYTICS)

def verify(user, pw):
    airtable = Airtable(BASE_ID, 'Authentication', API_KEY)
    user_data = airtable.search("ID", user)

    if user_data:
        user_password = user_data[0]["fields"]["Password"]
        if user_password == pw or os.getenv("MASTER_PASS") == pw:
            return user_data[0]["fields"]["ID"]
    
    return False

def log_user_activity(uid, endpoint, timestamp):
    timestrfmt = "%B %d, %Y %I:%M:%S %p %Z"
    log = {
        "uid": uid,
        "endpoint": endpoint,
        "timestamp": timestamp.strftime(timestrfmt)
    }

    log_table = Airtable(BASE_ID, 'Activity Logs', API_KEY)
    log_table.insert(log)

def log_error(uid, endpoint, timestamp, desc):
    timestrfmt = "%B %d, %Y %I:%M:%S %p %Z"
    err_log = {
        "uid": uid,
        "endpoint": endpoint,
        "timestamp": timestamp.strftime(timestrfmt),
        "description": desc
    }

    err_log_table = Airtable(BASE_ID, 'Error Logs', API_KEY)
    err_log_table.insert(err_log)

@app.route('/github_webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('./')
        origin = repo.remotes.origin
        origin.pull()
        return '', 200
    else:
        return '', 400

@app.route('/_post_tz/', methods=['POST'])
def post_tz():    
    data = request.get_json()

    session["timezone"] = data['timezone']
    session["offset"] = data['offset']
    session["tz_region"] = data['region']

    return ('', 204)

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)

    if user_id:
        log_user_activity(user_id, "/", timestamp)
        return render_template("index.html")
    
    return redirect(url_for("login"))

@app.route('/support')
def support():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)

    if user_id:
        log_user_activity(user_id, "/support", timestamp)
    else:
        log_user_activity(-1, "/support", timestamp)
    
    return render_template("support.html")

@app.route('/facilitators')
def facilitators():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)

    if user_id:
        if user_id < 1010:
            resources = Airtable(BASE_ID, 'Facilitator Resources', API_KEY).get_iter(sort=['Order'])
            log_user_activity(user_id, "/facilitators", timestamp)

            return render_template("facilitators.html", resources=resources)
        else:
            return redirect("/")
    
    return redirect("/")

@app.route('/resources')
def resources():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)

    if user_id:
        resources = Airtable(BASE_ID, 'Resources', API_KEY).get_iter(sort=['Order'])
        log_user_activity(user_id, "/resources", timestamp)

        return render_template("resources.html", resources=resources)

    return redirect(url_for("login"))

@app.route('/profile')
def profile():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)

    if user_id:
        if user_id < 1010:
            user_info = Airtable(BASE_ID, 'Facilitator', API_KEY).search("ID", user_id)[0]["fields"]
        else:
            user_info = Airtable(BASE_ID, 'Participant', API_KEY).search("ID", user_id)[0]["fields"]
        
        family_info = Airtable(BASE_ID, 'Family', API_KEY)
        cabin_info = Airtable(BASE_ID, 'Cabin', API_KEY)
        eco_info = Airtable(BASE_ID, 'Eco', API_KEY)
        create_info = Airtable(BASE_ID, 'Create', API_KEY)
        
        if user_id < 1010:
            data = {
                    "Name": user_info["Full Name"][0],
                }
            if "Family" in user_info:
                data["Family"] = family_info.get(user_info["Family"][0])["fields"]["Name"]
            if "Cabin" in user_info:
                data["Cabin"] = cabin_info.get(user_info["Cabin"][0])["fields"]["Cabin Name"]
        else:
            data = {
                "Name": user_info["Participant Name"][0],
                "Family": family_info.get(user_info["Family"][0])["fields"]["Name"],
                "Cabin": cabin_info.get(user_info["Cabin"][0])["fields"]["Cabin Name"],
                "Cabin Facilitator(s)": cabin_info.get(user_info["Cabin"][0])["fields"]["Facilitators Names"],
                "Create": create_info.get(user_info["Create Room"][0])["fields"]["Workshop Name"],
                "Eco Workshop": eco_info.get(user_info["EcoWorkshop"][0])["fields"]["EcoName"],
                "Eco Workshop Facilitator(s)": eco_info.get(user_info["EcoWorkshop"][0])["fields"]["Fac Name"]
            }

        log_user_activity(user_id, "/profile", timestamp)

        return render_template("profile.html", user_data=data)

    return redirect(url_for("login"))

@app.route('/login', methods = ["GET", "POST"])
def login():
    timestamp = datetime.now(tz=utc)
    data = {
        "invalid": False
    }

    if request.method == 'POST':
        user = request.form.get("id")
        pw = request.form.get("pw")

        uid = verify(user, pw)

        if uid:
            log_user_activity(uid, "/login", timestamp)
            session["user"] = uid
            return redirect(url_for("index"))

        data["invalid"] = True
        return render_template("login.html", data=data)
    
    user_id = session.get("user", None)
    if user_id:
        return redirect(url_for("index"))
    
    return render_template("login.html", data=data)

@app.route('/logout')
def logout():
    timestamp = datetime.now(tz=utc)
    session.pop("timezone", None)
    session.pop("offset", None)
    user_id = session.pop("user", None)

    if user_id:
        log_user_activity(user_id, "/logout", timestamp)

    return(redirect(url_for("login")))

@app.route('/certificate')
def certificate():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)

    if user_id:
        user_info = None
        name = None

        if user_id < 1010:
            user_info = Airtable(BASE_ID, 'Facilitator', API_KEY).search("ID", user_id)[0]["fields"]
            name = user_info["Full Name"][0]
        else:
            user_info = Airtable(BASE_ID, 'Participant', API_KEY).search("ID", user_id)[0]["fields"]
            name = user_info["Participant Name"][0]
        
        family = Airtable(BASE_ID, 'Family', API_KEY).get(user_info["Family"][0])["fields"]["Name"]

        log_user_activity(user_id, "/certificate", timestamp)

        return render_template("certificate.html", name=name, family=family)

    return redirect(url_for("login"))


#function to create html anchors
def htmlanchor(link):
    if link=='Visit HelpDesk':
        return "<a href='https://link.campconnect.co/helpdesk' target='_blank'>" + link + "</a>"
    elif link=='lounge':
        return '<a href="#lounge">Lounge Links</a>'
    return "<a href='" + link + "' target='_blank'>" + link + "</a>"

@app.route('/schedules', methods=['GET', 'POST'])
def schedules():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)

    if user_id:
        log_user_activity(user_id, "/schedules", timestamp)
        
        user_tbl = 'Facilitator'
        if(user_id>2999):
            user_tbl = 'Participant'

        user_data = {}
        for page in Airtable(BASE_ID, user_tbl, API_KEY).get_iter(formula=f"{{ID}}={user_id}"):
            for record in page:
                user_data["stagger"] = record['fields']['Stagger'][0]
                user_data["familyLink"] = record['fields']['FamilyLink'][0] if ('FamilyLink' in record['fields']) else 'Visit HelpDesk'
                if(user_data["stagger"] == 'C'):
                    user_data["familyLink2"] = record['fields']['JodavCombinedLink'][0] if ('JodavCombinedLink' in record['fields']) else 'Visit HelpDesk'
                user_data["cabinLink"] = record['fields']['CabinLink'][0] if ('CabinLink' in record['fields']) else 'Visit HelpDesk'
                user_data["createLink"] = record['fields']['CreateLink'][0] if ('CreateLink' in record['fields']) else 'Visit HelpDesk'
                user_data["ecoLink"] = record['fields']['EcoZoomLink'][0] if ('EcoZoomLink' in record['fields']) else 'Visit HelpDesk'
                user_data["family"] = record['fields']['FamName'][0][1] if ('Family' in record['fields']) else 'Visit HelpDesk'
                if(user_data["stagger"] == 'C'):
                    user_data["family"] = '10'
                user_data["timezone"] = session.get("timezone", None) if session.get("timezone", None) else 'UTC'
                user_data["offset"] = -1 * session.get("offset", None) if session.get("offset", None) else 0 #momentjs returns the inverse value
                # user_data["familyName"] = record['fields']['Family'][0] if ('Family' in record['fields']) else 'no'
                if(user_data["stagger"] == 'C'):
                    user_data["cabinLink2"] = record['fields']['JodavCabinLink'][0] if ('JodavCabinLink' in record['fields']) else 'Visit HelpDesk'
                    user_data["timezone"] = 'AFG'
                    user_data["offset"] = 270

        # print(user_data["family"])
        orientation_day = os.getenv("ORIENTATION" + user_data["stagger"] + "_START_DATETIME")
        camp_start = os.getenv("STAGGER" + user_data["stagger"] + "_START_DATETIME")

        orientation = datetime.strptime(orientation_day, '%Y-%m-%d %H:%M')
        startdate = datetime.strptime(camp_start, '%Y-%m-%d %H:%M')

        formula = f'AND({{Stagger}}=\"{user_data["stagger"]}\",{{Hidden}}!=1,{{FacOnly}}!=1)'
        if(user_id<3000):
            formula = f'AND({{Stagger}}=\"{user_data["stagger"]}\",{{Hidden}}!=1)'
            if(user_data["stagger"]=='C'):
                startdate = startdate + timedelta(minutes=-30)
            else:
                startdate = startdate + timedelta(hours=-1)

        #get sch data using ppant stagger
        schedule_tbl = os.getenv("SCHEDULE_TABLE") if os.getenv("SCHEDULE_TABLE") else 'Schedule'
        schInfo = Airtable(BASE_ID, schedule_tbl, API_KEY).get_all(formula=formula,sort=['Day', 'Order'])

        #list that will store organize the schData objects for the table
        schArr = []

        #camp start date for stagger and duration tracker
        durTracker = datetime.now()

        #stagger c counter for cabin opening links
        c_count = 1

        #day tracker 
        day = -1
        for record in schInfo:
            schData = {}

            #DateTime Ranges
            duration = schInfo[len(schArr)]['fields']['Duration']

            if day != schInfo[len(schArr)]['fields']['Day']:
                day = schInfo[len(schArr)]['fields']['Day']
                if day == 0:
                    durTracker = orientation + timedelta(minutes=user_data["offset"])
                else:
                    durTracker = startdate + timedelta(days=(day-1), minutes=user_data["offset"])

            schData[1] = durTracker
            durTracker = durTracker + timedelta(minutes=duration)
            schData[0] = datetime.strftime(schData[1], "%b %-d")
            schData[1] = datetime.strftime(schData[1], "%I:%M %p") + ' - ' + datetime.strftime(durTracker, "%I:%M %p") + ' ' + user_data["timezone"]

            #Activity
            location = schInfo[len(schArr)]['fields']['ActivityType']
            schData[2] = schInfo[len(schArr)]['fields']['Description'] if 'Description' in schInfo[len(schArr)]['fields'] else location

            #Zoom Link
            if 'cabin' in str.lower(location):
                if user_data["stagger"] != 'C':
                    schData[3] = htmlanchor(user_data["cabinLink"])
                else:
                    if c_count%3 != 0:
                        schData[3] = htmlanchor(user_data["cabinLink2"])
                    else:
                        schData[3] = htmlanchor(user_data["cabinLink"])
                    c_count += 1
            elif 'transition' in str.lower(location):
                schData[3] = 'Transition'
            elif 'combinedfamily' in str.lower(location):
                    schData[3] = htmlanchor(user_data["familyLink2"])
            elif 'family' in str.lower(location):
                    schData[3] = htmlanchor(user_data["familyLink"])
            elif 'break' in str.lower(location):
                schData[3] = htmlanchor('lounge')
            elif 'create' in str.lower(location):
                schData[3] = htmlanchor(user_data["createLink"])
            elif 'eco' in str.lower(location):
                schData[3] = htmlanchor(user_data["ecoLink"])
            elif 'briefing' in str.lower(location):
                schData[3] = htmlanchor("https://campconnect-co.zoom.us/my/connectfcd" + user_data["family"])
            elif 'WebinarLink' in schInfo[len(schArr)]['fields']:
                schData[3] = htmlanchor(schInfo[len(schArr)]['fields']['WebinarLink'])
            else:
                schData[3] = schData[2]
            
            schData[4] = schInfo[len(schArr)]['fields']['Day']
            schArr.append(schData)

        #get camp day #, default to 1
        campday = (datetime.utcnow().day % 25) if 0<(datetime.utcnow().day % 26)<7 else 1
        region = session.get("tz_region", None) if session.get("tz_region", None) else "Etc/UTC"
        if (user_data["stagger"]=='C'):
            region = 'Asia/Kabul'

        # get family for jodav notice 
        farsi = ( user_data["stagger"] == 'C' )

        return render_template('schedules.html', data=schArr, campday=campday, tz=user_data["timezone"], tz_region=region, farsi=farsi)
    
    return redirect(url_for("login"))

@app.errorhandler(401)
def FUN_401(error):
    return render_template("401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    uid = session.get("user", None)

    if not uid:
        uid = -1

    time = datetime.now(tz=utc)
    log_error(uid, request.path, time, str(error))
    return render_template("404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    uid = session.get("user", None)

    if not uid:
        uid = -1

    time = datetime.now(tz=utc)
    log_error(uid, request.path, time, str(error))
    return render_template("405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    uid = session.get("user", None)

    if not uid:
        uid = -1

    time = datetime.now(tz=utc)
    log_error(uid, request.path, time, str(error))
    return render_template("413.html"), 413

@app.errorhandler(500)
def FUN_500(error):
    print("500 Error!!")
    uid = session.get("user", None)

    if not uid:
        uid = -1

    time = datetime.now(tz=utc)
    log_error(uid, request.path, time, str(error))
    return render_template("500.html"), 500    

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
