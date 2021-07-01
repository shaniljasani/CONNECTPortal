import requests
import os
import urllib.parse
import json
import pytz
import git

from flask import Flask, render_template, send_from_directory, url_for, request, redirect, session



# set the "static" directory as the static folder
app = Flask(__name__, static_url_path='/static')

@app.route('/support')
def support():
    return render_template("support.html")

@app.route('/schedules')
def schedules():
    return render_template('comingsoon.html')

@app.route('/resources')
def resources():
    return render_template('comingsoon.html')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('comingsoon.html')

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
