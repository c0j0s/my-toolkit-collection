from notion.collection  import NotionDate 
from notionUtils import Detail, NotionUtils
from dangdangUtils import DangDangUtils
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import atexit
import traceback
import os

def gen_table_row_callback(record, changes):
    if changes[0][0] is "prop_changed":
        start = record.start_task
        record.start_task = False
        if start and record.source is not "" and record.status == "Not Started":
            log("Detail generation task starting: " + record.title)
            record.status = "Processing"
            try:
                log("Detail generation task in progress")
                record.result = notion.insertDetailToNotion(record.source)
                record.status = "Completed"
                log("Detail generation task completed!")
            except Exception as e:
                record.status = "Error"
                log("Detail generation task error: " + str(e))
        time.sleep(3)

def genReportingText(veh_type,mid,avi,fe):
    return "1 x {} moving off from [] to []\nMID : {}\nTO : LCP JUN SHENG\nVC : []\nAVI : {}\nFE : {}\nPurpose : []".format(veh_type,mid,avi,fe)

def boc_collection_row_callback(record, changes):
    if changes[0][0] is "prop_changed":
        if record.status != "Not Started" and record.status != "Cancelled":
            if record.avi is not "" and record.fe is not "" and not record.generate_reporting_text and record.done_on is None:
                if record.status == "Pass":
                    log("Boc status passed, starting sequence...")
                    mid = record.for_detail[0].assigned_vehicle[0].mid
                    veh_type = record.for_detail[0].assigned_vehicle[0].vehicle_type_ref[0].vehicle_type
                    record.for_detail[0].reporting_template = genReportingText(veh_type,mid,record.avi,record.fe)
                    record.generate_reporting_text = True
                    log("Boc status passed, Done")
                
                record.done_on = NotionDate(datetime.now())
            else:
                if record.status == "Pass" and record.avi is "" and record.fe is  "":
                    record.status = "Not Started"
                    log("Boc status invalid action")
        else:
            if record.generate_reporting_text:
                record.generate_reporting_text = False
                log("Boc status invalid action")
        time.sleep(3)

def config_callback(record, changes):
    if changes[0][0] is "prop_changed":
        notion.setConfig(record.group,record.name,record.value)
    time.sleep(3)

def init():
    # config_path = "/home/opc/notion-py-api/config.json"
    config_path = "./config.json"

    global notion, collections
    notion = NotionUtils(config_path,monitor=True,start_monitoring=True)
    collections = {}

    log("Initialising Configs")
    count = 0
    for row in notion.getTable("config").get_rows():
        if row.name is not "":
            notion.setConfig(row.group,row.name,row.value)
            row.add_callback(config_callback, callback_id="config_callback")
            count += 1

    collections["gen_task"] = notion.getTable("detail_gen_task")
    collections["detail"] = notion.getTable("detail_list")
    collections["boc"] = notion.getTable("boc_record")
    collections["debug"] = notion.getTable("debug_log")
    log("{} configs loaded".format(str(count)))

    log("Registering schedule task")
    cron = BackgroundScheduler(daemon=True)
    cron.add_job(dangDailySignIn,'interval',hours=24)
    cron.start()
    atexit.register(lambda: cron.shutdown(wait=False))
    log("Registering schedule task completed")

def main():
    log("Notion Task Handler Started")
    try:
        log("Registering detail generation task table row callbacks")
        for row in collections["gen_task"].get_rows():
            row.add_callback(gen_table_row_callback, callback_id="gen_table_row_callback")

        log("Registering boc table row callbacks")
        for row in collections["boc"].get_rows():
            row.add_callback(boc_collection_row_callback, callback_id="boc_collection_row_callback")

        log("Ready and listening! (Ctrl-C to exit/Enter exit)")
        command = ""
        while True:
            command = str(input("Command: "))
            if command == "signin":
                dangDailySignIn()
            if command == "exit":
                raise KeyboardInterrupt()

    except Exception as e:
        log(e)
        pass
    except KeyboardInterrupt as e:
        log("Program Exit")
        exit()

def dangDailySignIn():
    log("Dang daily sign in started")
    dangdangUtil = DangDangUtils(notion.getProperty("dang_endpoint"),notion.getProperty('dang_token'))
    notion.insertSignInRecord(dangdangUtil.dailySignIn())
    log("Dang daily sign in done")

def log(msg):
    print("[{}][{}]: {}".format(pid,datetime.now(),str(msg)))
    try:
        if notion.getProperty("debug").upper() == "TRUE":
            row = collections["debug"].add_row()
            row.pid = str(pid)
            row.time = NotionDate(datetime.now())
            row.message = str(msg)
    except:
        pass

if __name__ == "__main__":
    global pid
    pid = os.getpid()

    log("Notion Task Handler Started")
    init()
    main()