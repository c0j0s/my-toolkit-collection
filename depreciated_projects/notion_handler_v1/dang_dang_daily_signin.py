"""
This is a script service that auto sign in everyday to dangdang everyday for silver coins.
Abandon as silver coins is only valid for 7 days by nature.

Author: COJOS
"""


from notion.client import NotionClient
from task_handler import TaskHandler
import requests
import sys
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

dang_endpoint = "<REMOVED>"
dang_token = "<REMOVED>"
dang_log = "<REMOVED>"

handler = TaskHandler(sys.argv[1])
client = NotionClient(token_v2=handler.configs["token"])

def insert_sign_in_record(result):
	cv = client.get_collection_view(dang_log).collection
	row = cv.add_row()
	
	if result["status"]["code"] == 0:
	    row.result = str(result["data"]["tips"])
	    row.value = int(result["data"]["bellPrize"])
	elif result["status"]["code"] == 30001 or result["status"]["code"] == 10003:
	    row.result = str(result["status"]["message"])
	    row.value = 0

def get(PARAMS):
	PARAMS["token"] = dang_token
	PARAMS["deviceType"] = "Android"
	result = requests.get(url=dang_endpoint, params=PARAMS)
	return result.json()
	#return {"status": {"code": 30001,"message":"test"}}

def dang_daily_sign_in():
	handler.print("Dang daily sign in started")
	insert_sign_in_record(get({'action': 'signin'}))
	handler.print("Dang daily sign in sequence completed")

cron = BackgroundScheduler(daemon=True)
cron.add_job(dang_daily_sign_in, 'cron', hour=1)
cron.start()
atexit.register(lambda: cron.shutdown(wait=False))

while True:
	pass