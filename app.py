from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# set the "static" directory as the static folder
app = Flask(__name__, static_url_path='/static')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/logout')
def logout():
    return render_template("login.html")

@app.route('/resources')
def resources():
    return render_template("resources.html")

@app.route('/schedules')
def schedules():
    return render_template("schedules.html")

@app.route('/forgot-password')
def forgotPassword():
    return render_template("forgot-password.html")

if __name__ == "__main__":
    app.run(debug=True, host="localhost")