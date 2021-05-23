from notion.collection import NotionDate
from NotionWrapper import Detail, NotionWrapper
from DangDangUtils import DangDangUtils
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import atexit
import traceback
import os

def gen_table_row_callback(record, changes):
    if changes[0][0] == "prop_changed":
        start = record.start_task
        record.start_task = False
        if start and record.source != "" and record.status == "Not Started":
            log("Detail generation task starting: " + record.title)
            record.status = "Processing"
            try:
                log("Detail generation task in progress")
                record.result = notion.insert_detail_to_notion(record.source)
                record.status = "Completed"
                log("Detail generation task completed!")
            except Exception as e:
                record.status = "Error"
                log("Detail generation task error: " + str(e))
        time.sleep(3)

def gen_reporting_text(veh_type, mid, avi, fe):
    return "1 x {} moving off from [] to []\nMID : {}\nTO : LCP <REMOVED>\nVC : []\nAVI : {}\nFE : {}\nPurpose : []".format(veh_type, mid, avi, fe)

def boc_collection_row_callback(record, changes):
    if changes[0][0] == "prop_changed":
        if record.status != "Not Started" and record.status != "Cancelled":
            if record.avi != "" and record.fe != "" and not record.generate_reporting_text and record.done_on == None:
                if record.status == "Pass":
                    log("Boc status passed, starting sequence...")
                    mid = record.for_detail[0].assigned_vehicle[0].mid
                    veh_type = record.for_detail[0].assigned_vehicle[0].vehicle_type_ref[0].vehicle_type
                    record.for_detail[0].reporting_template = gen_reporting_text(
                        veh_type, mid, record.avi, record.fe)
                    record.generate_reporting_text = True
                    log("Boc status passed, Done")

                record.done_on = NotionDate(datetime.now())
            else:
                if record.status == "Pass" and record.avi == "" and record.fe == "":
                    record.status = "Not Started"
                    log("Boc status invalid action")
        else:
            if record.generate_reporting_text:
                record.generate_reporting_text = False
                log("Boc status invalid action")
        time.sleep(3)


def config_callback(record, changes):
    if changes[0][0] == "prop_changed":
        notion.set_config(record.group, record.name, record.value)
    time.sleep(3)


def init():
    config_path = "/home/opc/notion-py-api/config.json"
    # config_path = "./config.json"

    global notion, collections
    notion = NotionWrapper(config_path, monitor=True, start_monitoring=True)
    collections = {}

    log("Initialising Configs")
    count = 0
    for row in notion.get_table("config").get_rows():
        if row.name != "":
            notion.set_config(row.group, row.name, row.value)
            row.add_callback(config_callback, callback_id="config_callback")
            count += 1

    collections["gen_task"] = notion.get_table("detail_gen_task")
    collections["detail"] = notion.get_table("detail_list")
    collections["boc"] = notion.get_table("boc_record")
    collections["debug"] = notion.get_table("debug_log")
    log("{} configs loaded".format(str(count)))

    log("Registering schedule task")
    cron = BackgroundScheduler(daemon=True)
    cron.add_job(dang_daily_sign_in, 'cron', hour=1)
    cron.start()
    atexit.register(lambda: cron.shutdown(wait=False))
    log("Registering schedule task completed")


def main():
    log("Notion Task Handler Started")
    try:
        log("Registering detail generation task table row callbacks")
        for row in collections["gen_task"].get_rows():
            row.add_callback(gen_table_row_callback,
                             callback_id="gen_table_row_callback")

        log("Registering boc table row callbacks")
        for row in collections["boc"].get_rows():
            row.add_callback(boc_collection_row_callback,
                             callback_id="boc_collection_row_callback")

        log("Ready and listening! (Ctrl-C to exit/Enter exit)")
        command = ""
        while True:
            command = str(input("Command: "))
            if command == "signin":
                dang_daily_sign_in()
            if command == "exit":
                raise KeyboardInterrupt()

    except Exception as e:
        log(e)
        pass
    except KeyboardInterrupt as e:
        log("Program Exit")
        exit()


def dang_daily_sign_in():
    log("Dang daily sign in started")
    dangdangUtil = DangDangUtils(notion.get_property(
        "dang_endpoint"), notion.get_property('dang_token'))
    notion.insert_sign_in_record(dangdangUtil.daily_sign_in())
    log("Dang daily sign in sequence completed")


def log(msg):
    print("[{}][{}]: {}".format(pid, datetime.now(), str(msg)))
    try:
        if notion.get_property("debug").upper() == "TRUE":
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
