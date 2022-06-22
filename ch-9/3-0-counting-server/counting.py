import json

import robot_wifi

from adafruit_wsgi.wsgi_app import WSGIApp

app = WSGIApp()

counter = iter(range(int(1e6)))

@app.route("/")
def index(request):
    with open("counting.html") as fd:
        hello_html = fd.read()
    return 200, [("Content-Type", "text/html")], hello_html

@app.route("/count")
def get_count(request):
    value = next(counter)
    print(f"Counter value is {value}")
    return 200, [("Content-Type", "application/json")], [json.dumps(value)]

robot_wifi.start_wifi_server(app)
