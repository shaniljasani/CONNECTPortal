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

if __name__ == "__main__":
    app.run(debug=True, host="localhost")