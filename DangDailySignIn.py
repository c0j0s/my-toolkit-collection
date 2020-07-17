from notion.client import NotionClient
from task_handler import TaskHandler
import requests
import sys
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

dang_endpoint = "http://e.dangdang.com/media/api2.go"
dang_token = "e_d1e0587145a16f6bdac2422da1260b67b79b0abd5873f6dcc887a02f00dd9d1"
dang_log = "https://www.notion.so/c0j0s/23b2b678e9d44e72872a6dc331f3e398?v=141d1a847c2a4fc481b2f61c1cdc8e64"

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

#Second Code Block

