import sys
import json
import logging
from flask import Flask
from notion_controller import NotionController

app = Flask(__name__)
headers = {}

@app.route("/nscalendar/<access>")
def nscalendar(access):
    if str(access) == config["access_token"]:
        result = controller.get_ns_events()
        headers['Content-Type'] = 'text/calendar;charset=utf-8'
        headers['Content-Disposition'] = 'attachment;filename=calendar.ics'
        return (result, 200, headers)
    else:
        return 404

@app.route("/ptcalender/<access>")
def ptcalender(access):
    if str(access) == config["access_token"]:
        result = controller.get_pt_schedule()
        headers['Content-Type'] = 'text/calendar;charset=utf-8'
        headers['Content-Disposition'] = 'attachment;filename=calendar.ics'
        return (result, 200, headers)
    else:
        return 404

if __name__ == "__main__":
    global config, controller

    with open(sys.argv[1]) as json_f:
        config = json.load(json_f)
        logging.basicConfig(filename=config["log_file"], level=logging.INFO, format=config["log_format"])
        controller = NotionController(config["notion_token"], debug=config["debug"])
        app.run(host=config["host"], port=config["port"])