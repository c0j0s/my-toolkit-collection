"""
This is a simple script for calucalting 2.4km running time based on each running session.
It is made obsolete as of 05/09/2020, replaced by table formula instead.

Author: COJOS
"""

from notion.client import NotionClient
from task_handler import TaskHandler
import time
import sys
import math
import json

sleep = 5
handler = TaskHandler(sys.argv[1])
handler.configs["ippt_table"] = "<REMOVED>"
client = NotionClient(token_v2=handler.configs["token"], monitor=True, start_monitoring=True)

def ippt_row_callback(record, changes):
    if changes[0][0] == "prop_changed" and str(changes[0][2][1]) == "True":
        start = record.calculate
        record.calculate = False
        if start and record.running == "":
            handler.print("Ippt handler generating results.")
            if record.push_up == "":
                record.push_up = 0
            if record.sit_up == "":
                record.sit_up = 0
            if record.running_distance == "":
                record.running_distance == 3
            if record.running_time == "":
                record.running_time == 20

            estimated_2_4 = 2400 / ((record.running_distance * 1000)/(record.running_time * 60))
            runMins = estimated_2_4 // 60
            runSecs = estimated_2_4 % 60
            record.running = "{:02d}:{:02d}".format(int(runMins), int(runSecs))
        time.sleep(sleep)

def ippt_table_callback(record, difference, changes):
    for item in difference:
        if item[0] == "add":
            for row in record.collection.get_rows():
                row.remove_callbacks("ippt_row_callback")
                row.add_callback(ippt_row_callback,
                                 callback_id="ippt_row_callback")
        break
    time.sleep(sleep)


def main():
    ippt_table = client.get_collection_view(handler.configs["ippt_table"])
    ippt_table.add_callback(ippt_table_callback,
                            callback_id="ippt_table_callback")
    for row in ippt_table.collection.get_rows():
        row.add_callback(ippt_row_callback, callback_id="ippt_row_callback")

    handler.print("Ippt handler ready.")
    while True:
        pass


if __name__ == "__main__":
    main()
