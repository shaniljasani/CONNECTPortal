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
app.url_map.strict_slashes = False

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("BASE_ID")
G_ANALYTICS = os.getenv("G_ANALYTICS")

@app.context_processor
def inject_analytics():
    return dict(analytics_id=G_ANALYTICS)

@app.before_request
def clear_trailing():
    rp = request.path 
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1])

def verify(user, pw):
    user_tbl = 'Facilitators & Staff'
    if(int(user)>3999 and int(user)<9000):
        user_tbl = 'Participants'
    airtable = Airtable(BASE_ID, user_tbl, API_KEY)
    user_data = airtable.search("ID", user)

    if user_data:
        user_password = user_data[0]["fields"]["Password"] if 'Password' in user_data[0]["fields"] else None
        if user_password == pw or os.getenv("MASTER_PASS") == pw:
            return user_data[0]["fields"]["ID"]
    
    return False

def get_camp(uid):
    user_tbl = 'Facilitators & Staff'
    if(int(uid)>3999 and int(uid)<9000):
        user_tbl = 'Participants'
    user_data = Airtable(BASE_ID, user_tbl, API_KEY).get_all(fields=['Theme'], formula=f"{{ID}}={uid}")
    session["theme"] = user_data[0]["fields"]["Theme"]
    if 'PT1' in user_data[0]["fields"]["Theme"]:
        session["theme"] = 'PT1 ET'
    if 'PT2' in user_data[0]["fields"]["Theme"]:
        session["theme"] = 'PT2 HW'

# def log_user_activity(uid, endpoint, timestamp):
#     timestrfmt = "%B %d, %Y %I:%M:%S %p %Z"
#     log = {
#         "uid": uid,
#         "endpoint": endpoint,
#         "timestamp": timestamp.strftime(timestrfmt)
#     }

#     log_table = Airtable(BASE_ID, 'Activity Logs', API_KEY)
#     log_table.insert(log)

# def log_error(uid, endpoint, timestamp, desc):
#     timestrfmt = "%B %d, %Y %I:%M:%S %p %Z"
#     err_log = {
#         "uid": uid,
#         "endpoint": endpoint,
#         "timestamp": timestamp.strftime(timestrfmt),
#         "description": desc
#     }

#     err_log_table = Airtable(BASE_ID, 'Error Logs', API_KEY)
#     err_log_table.insert(err_log)

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
@app.route('/_post_tz', methods=['POST'])
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
        #log_user_activity(user_id, "/", timestamp)
        return render_template("index.html")
    
    return redirect(url_for("login"))

@app.route('/support')
def support():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)
    # if user_id:
    #     log_user_activity(user_id, "/support", timestamp)
    # else:
    #     log_user_activity(-1, "/support", timestamp)
    
    return render_template("support.html")

# @app.route('/facilitators')
# def facilitators():
#     user_id = session.get("user", None)
#     timestamp = datetime.now(tz=utc)

#     if user_id:
#         if user_id < 1010:
#             resources = Airtable(BASE_ID, 'Facilitator Resources', API_KEY).get_iter(sort=['Order'])
#             #log_user_activity(user_id, "/facilitators", timestamp)

#             return render_template("facilitators.html", resources=resources)
#         else:
#             return redirect("/")
    
#     return redirect("/")

@app.route('/resources')
def resources():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)
    theme = session.get("theme", None)

    if user_id:
        resource_tbl = 'Staff Resources'
        if(user_id>3999 and user_id<9000):
            resource_tbl = 'Participant Resources'

        resources = Airtable(BASE_ID, resource_tbl, API_KEY).get_iter(view=theme)
        #log_user_activity(user_id, "/resources", timestamp)

        return render_template("resources.html", resources=resources)

    return redirect(url_for("login"))

# @app.route('/profile')
# def profile():
#     user_id = session.get("user", None)
#     timestamp = datetime.now(tz=utc)

#     if user_id:
#         if user_id < 1010:
#             user_info = Airtable(BASE_ID, 'Facilitator', API_KEY).search("ID", user_id)[0]["fields"]
#         else:
#             user_info = Airtable(BASE_ID, 'Participant', API_KEY).search("ID", user_id)[0]["fields"]
        
#         family_info = Airtable(BASE_ID, 'Family', API_KEY)
#         cabin_info = Airtable(BASE_ID, 'Cabin', API_KEY)
#         eco_info = Airtable(BASE_ID, 'Eco', API_KEY)
#         create_info = Airtable(BASE_ID, 'Create', API_KEY)
        
#         if user_id < 1010:
#             data = {
#                     "Name": user_info["Full Name"][0],
#                 }
#             if "Family" in user_info:
#                 data["Family"] = family_info.get(user_info["Family"][0])["fields"]["Name"]
#             if "Cabin" in user_info:
#                 data["Cabin"] = cabin_info.get(user_info["Cabin"][0])["fields"]["Cabin Name"]
#         else:
#             data = {
#                 "Name": user_info["Participant Name"][0],
#                 "Family": family_info.get(user_info["Family"][0])["fields"]["Name"],
#                 "Cabin": cabin_info.get(user_info["Cabin"][0])["fields"]["Cabin Name"],
#                 "Cabin Facilitator(s)": cabin_info.get(user_info["Cabin"][0])["fields"]["Facilitators Names"],
#                 "Create": create_info.get(user_info["Create Room"][0])["fields"]["Workshop Name"],
#                 "Eco Workshop": eco_info.get(user_info["EcoWorkshop"][0])["fields"]["EcoName"],
#                 "Eco Workshop Facilitator(s)": eco_info.get(user_info["EcoWorkshop"][0])["fields"]["Fac Name"]
#             }

#         #log_user_activity(user_id, "/profile", timestamp)

#         return render_template("profile.html", user_data=data)

#     return redirect(url_for("login"))

@app.route('/login', methods = ["GET", "POST"])
def login():
    timestamp = datetime.now(tz=utc)
    data = {
        "invalid": False
    }

    if request.method == 'POST':
        user = request.form.get("id")
        pw = request.form.get("pw")

        uid = int(verify(user, pw))

        if uid:
            #log_user_activity(uid, "/login", timestamp)
            session["user"] = uid
            get_camp(uid)
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

    # if user_id:
        #log_user_activity(user_id, "/logout", timestamp)

    return(redirect(url_for("login")))

@app.route('/certificate')
def certificate():
    user_id = session.get("user", None)
    timestamp = datetime.now(tz=utc)

    if user_id:
        user_info = None
        name = None

        # if user_id < 1010:
        #     user_info = Airtable(BASE_ID, 'Facilitator', API_KEY).search("ID", user_id)[0]["fields"]
        #     name = user_info["Full Name"][0]
        # else:
        #     user_info = Airtable(BASE_ID, 'Participant', API_KEY).search("ID", user_id)[0]["fields"]
        #     name = user_info["Participant Name"][0]

        #log_user_activity(user_id, "/certificate", timestamp)

        # return render_template("certificate.html", name=name)
        return render_template("certificate.html")


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
    theme = session.get("theme", None)
    timestamp = datetime.now(tz=utc)

    # ZOOM_DOMAIN = os.getenv("ZOOM_DOMAIN")
    
    PT1_LINK = os.getenv("PT1_LINK")
    PT2_LINK = os.getenv("PT2_LINK")

    if user_id:
        #log_user_activity(user_id, "/schedules", timestamp)
        
        user_tbl = 'Facilitators & Staff'
        if(user_id>3999 and user_id<9000):
            user_tbl = 'Participants'

        user_data = {}
        for page in Airtable(BASE_ID, user_tbl, API_KEY).get_iter(formula=f"{{ID}}={user_id}"):
            for record in page:
                if user_tbl == 'Participants':
                    user_data["exploreLink"] = record['fields']['Explore ZoomURL'] if ('Explore ZoomURL' in record['fields']) else 'Visit HelpDesk'
                    user_data["cabinLink"] = record['fields']['Cabin ZoomURL'] if ('Cabin ZoomURL' in record['fields']) else 'Visit HelpDesk'
                    user_data["createLink"] = record['fields']['Create ZoomURL'] if ('Create ZoomURL' in record['fields']) else 'Visit HelpDesk'
                    user_data["gatherLink"] = record['fields']['Gather ZoomURL'] if ('Gather ZoomURL' in record['fields']) else 'Visit HelpDesk'
                else:
                    user_data["exploreLink"] = record['fields']['Explore ZoomURL'][0] if ('Explore ZoomURL' in record['fields']) else 'Visit HelpDesk'
                    user_data["cabinLink"] = record['fields']['Cabin ZoomURL'][0] if ('Cabin ZoomURL' in record['fields']) else 'Visit HelpDesk'
                    user_data["createLink"] = record['fields']['Create ZoomURL'][0] if ('Create ZoomURL' in record['fields']) else 'Visit HelpDesk'
                    user_data["gatherLink"] = record['fields']['Gather ZoomURL'][0] if ('Gather ZoomURL' in record['fields']) else 'Visit HelpDesk'
                user_data["family"] = record['fields']['Family'] if ('Family' in record['fields']) else 'Visit HelpDesk'
                user_data["timezone"] = session.get("timezone", None) if session.get("timezone", None) else 'UTC'
                user_data["offset"] = -1 * session.get("offset", None) if session.get("offset", None) else 0 #momentjs returns the inverse value
                # user_data["familyName"] = record['fields']['Family'][0] if ('Family' in record['fields']) else 'no'

        #orientation_day = os.getenv("ORIENTATION" + user_data["stagger"] + "_START_DATETIME")
        #orientation_day = os.getenv("ORIENTATION_START_DATETIME")
        #camp_start = os.getenv("STAGGER" + user_data["stagger"] + "_START_DATETIME")
        #camp_start = os.getenv("CAMP_START_DATETIME")

        formula = f'{{Hidden}}!=1'
        if(user_id>3999 and user_id<9000):
            formula = f'AND({{Hidden}}!=1,{{Fac Only}}!=1)'
            #startdate = startdate + timedelta(hours=-1)

        #get sch view
        schedule_tbl = 'Schedule: ' + theme
        #schedule_tbl = os.getenv("SCHEDULE_TABLE") if os.getenv("SCHEDULE_TABLE") else 'Schedule'
        #schInfo = Airtable(BASE_ID, schedule_tbl, API_KEY).get_all(formula=formula,sort=['Day', 'Order'])
        #schInfo = Airtable(BASE_ID, schedule_tbl, API_KEY).get_all(view=f'Build: {theme}')
        schInfo = Airtable(BASE_ID, schedule_tbl, API_KEY).get_all(formula=formula, view=theme)
        
        #orientation = datetime.strptime(orientation_day, '%Y-%m-%d %H:%M')
        #startdate = datetime.strptime(camp_start, '%Y-%m-%d %H:%M')
        startdate = datetime.strptime(schInfo[0]['fields']['Local Time'], '%Y-%m-%dT%H:%M:%S.000Z')
        
        #list that will store organize the schData objects for the table
        schArr = []

        #duration tracker
        durTracker = datetime.now()

        #day tracker 
        day = -1

        #account for transition
        transition_time = 0
        transition_flag = 0
        for record in schInfo:
            
            if record['fields']['Block'] == 'TRANSITION':
                transition_time = record['fields']['Duration']/60
                transition_flag = 1
                continue
            else:
                if transition_flag == 1:
                    transition_flag = 0
                else:
                    transition_time = 0


            schData = {}

            #DateTime Ranges
            #airtable is now returning the hour for some unknown reason
            duration = record['fields']['Duration']/60

            if day != record['fields']['Day']:
                day = record['fields']['Day']
                durTracker = startdate + timedelta(days=(int(day)-1), minutes=user_data["offset"])
                # if day == 0:
                #     durTracker = orientation + timedelta(minutes=user_data["offset"])
                # else:
                #     durTracker = startdate + timedelta(days=(int(day)-1), minutes=user_data["offset"])

            schData[1] = durTracker + timedelta(minutes=transition_time)
            durTracker = durTracker + timedelta(minutes=duration) + timedelta(minutes=transition_time)
            schData[0] = datetime.strftime(schData[1], "%b %-d")
            schData[1] = datetime.strftime(schData[1], "%I:%M %p") 
            #+ ' - ' + datetime.strftime(durTracker, "%I:%M %p") + ' ' + user_data["timezone"]

            #Activity
            type = record['fields']['Zoom URL Portal Sync'] if 'Zoom URL Portal Sync' in record['fields'] else 'error'
            schData[2] = record['fields']['Module Title'] if 'Module Title' in record['fields'] else type

            #Zoom Link
            if type == 'Cabin ZoomURL':
                schData[3] = htmlanchor(user_data["cabinLink"])
            elif type == 'Explore ZoomURL':
                schData[3] = htmlanchor(user_data["exploreLink"])
            elif type == 'Create ZoomURL':
                schData[3] = htmlanchor(user_data["createLink"])
            elif type == 'Gather ZoomURL':
                schData[3] = htmlanchor(user_data["gatherLink"])
            elif type == 'PT1':
                schData[3] = htmlanchor(PT1_LINK)
            elif type == 'PT2':
                schData[3] = htmlanchor(PT2_LINK)
            elif type == 'Lounge':
                schData[3] = htmlanchor('lounge')
            # elif type == 'FCD / PD Line':
            #     schData[3] = htmlanchor(ZOOM_DOMAIN + user_data["family"][0].lower() + 'fcd')
            elif type == 'External':
                schData[3] = htmlanchor(record['fields']['ExternalLink']) if 'ExternalLink' in record['fields'] else htmlanchor('Visit HelpDesk')
            elif record['fields']['Block'] == 'TRANSITION':
                schData[3] = 'Go To Next Line'
            else:
                schData[3] = schData[2]
            
            schData[4] = record['fields']['Day']
            schArr.append(schData)

        #get camp day #, default to 1
        campday = (datetime.utcnow().day % startdate.day) + 1 if 0<(datetime.utcnow().day % startdate.day)<7 else 1
        region = session.get("tz_region", None) if session.get("tz_region", None) else "Etc/UTC"

        return render_template('schedules.html', data=schArr, campday=campday, tz=user_data["timezone"], tz_region=region, l1 = os.getenv('L1_LINK'), l2 = os.getenv('L2_LINK'), l3 = os.getenv('L3_LINK'))
    
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
    #log_error(uid, request.path, time, str(error))
    return render_template("404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    uid = session.get("user", None)

    if not uid:
        uid = -1

    time = datetime.now(tz=utc)
    #log_error(uid, request.path, time, str(error))
    return render_template("405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    uid = session.get("user", None)

    if not uid:
        uid = -1

    time = datetime.now(tz=utc)
    #log_error(uid, request.path, time, str(error))
    return render_template("413.html"), 413

@app.errorhandler(500)
def FUN_500(error):
    print("500 Error!!")
    uid = session.get("user", None)

    if not uid:
        uid = -1

    time = datetime.now(tz=utc)
    #log_error(uid, request.path, time, str(error))
    return render_template("500.html"), 500    

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
