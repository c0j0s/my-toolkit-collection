from notion.client import NotionClient
from notion.collection import NotionDate
from notion.collection import CollectionRowBlock
from task_handler import TaskHandler
import json
import re
from datetime import datetime
import sys
import time
import traceback

sleep = 2


class Detail:
    def set_title(self, next_index):
        self.title = "Detail " + str(next_index)

    def set_ref(self, veh_ref, boc_ref, reporting_ref=None, destination_ref=None):
        self.veh_ref = veh_ref
        self.boc_ref = boc_ref
        self.reporting_ref = reporting_ref
        self.destination_ref = destination_ref

    def build_from_raw(self, arr, debug=False):
        for line in arr:
            try:
                if line.startswith("Supporting"):
                    if "for" in line:
                        self.supporting = re.findall(
                            r"(?<=:.)(.*)(?=.for)", line)[0].replace(r"\s", '').replace("\r", "")
                        self.purpose = re.findall(
                            r"(?<=for.)(.*)(?=)", line)[0].replace("\r", "")
                    else:
                        s = line.replace("Supporting: ", "").split(" ")
                        self.supporting = s[0]
                        self.purpose = " ".join(s[1:])
                elif line.startswith("Reporting"):
                    self.resporting = line.split(": ")[1].replace("\r", "")
                elif line.startswith("Destination"):
                    self.destination = []

                    dest_raw = line.split(": ")[1].replace("\r", "")
                    if "-" in dest_raw:
                        self.destination = dest_raw.split("-")
                    else:
                        self.destination.append(dest_raw)

                elif line.startswith("POC"):
                    self.poc = re.findall(
                        r"(?<=: )(.*)(?=\s?\([0-9])", line)[0]
                    self.poc_contact = re.findall(r"[0-9]{8}", line)[0]
                elif re.findall(r"..\/..\/..", line):
                    dates, hrs = ["", ""]

                    dates = re.findall(r"..\/..\/..", line)
                    hrs = re.findall(r"[0-9]{4}(?=hrs)", line)
                    self.start_date = dates[0]
                    self.start_time = hrs[0]
                    self.end_date = dates[1]
                    self.end_time = hrs[1]
                elif re.findall(r"(?=<REMOVED>.?<REMOVED> \()(.*)(?=\))", line):
                    self.veh_type = re.findall(
                        r"(?<=x )(.*)(?=:)", line)[0].upper()
                    mid = re.findall(
                        r"(?<=<REMOVED> \()(MID.?[0-9]{5})(?=\))", line)
                    if len(mid) == 0:
                        mid = re.findall(
                            r"(?<=<REMOVED> <REMOVED> \()(MID.?[0-9]{5})(?=\))", line)

                    # check again
                    assert len(mid) != 0, "Detail Mid Number Error"

                    self.mid = mid[0]
                    self.mid = self.mid.replace("MID", "")

            except Exception as e:
                print("{}:{}".format(e, line))

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_duration(self):
        assert self.end_date != "", "End date is not set"

        assert self.start_time != "" or self.end_time != "", "Start or end time is not set"

        date_format = '%d/%m/%y %H%M'
        start_datetime = self.start_date + " " + self.start_time
        end_datetime = self.end_date + " " + self.end_time
        duration_start = datetime.strptime(start_datetime, date_format)
        duration_end = datetime.strptime(end_datetime, date_format)

        return NotionDate(duration_start, duration_end)


class DetailUtils:

    def __init__(self, configs):
        self.configs = configs
        self.client = NotionClient(
            token_v2=self.configs["token"], monitor=True, start_monitoring=True)

    def pre_process_detail(self, rawInput):
        myDetail = []

        source = rawInput.split("\n")
        singleTmp = []

        detailCount = 1
        currentCount = 0
        for line in source:
            if re.findall(r"^[0-9]{2}(?!\S)", line):
                currentCount = int(line[:2])
                if currentCount < detailCount:
                    detailCount = 1
            else:
                if detailCount == currentCount:
                    singleTmp.append(line)

            if line.startswith("POC"):
                for line in singleTmp:
                    if re.findall(r"<REMOVED>.?<REMOVED>", line) or re.findall(r"<REMOVED>", line):
                        x = Detail()
                        x.build_from_raw(singleTmp)
                        myDetail.append(x)
                singleTmp = []
                detailCount += 1
        return myDetail

    def check_if_ref_exists(self, table, keyword):
        result = self.get_table(table).get_rows(search=keyword)

        if len(result) > 0:
            return result[0]
        else:
            return None

    # create new record: title:mid, type:ref
    def create_vehicle_md_type_record(self, mid, veh_type):
        # check if vehicle record exists
        veh_ref = self.check_if_ref_exists('veh_type_mid', mid)
        if veh_ref is not None and type(veh_ref) == CollectionRowBlock:
            return veh_ref

        # check if vehicle type is valid
        veh_type_ref = self.check_if_ref_exists('veh_types', veh_type)
        assert veh_type_ref is not None, "Unknown Vehicle Type"

        cv = self.get_table('veh_type_mid')
        row = cv.add_row()
        row.icon = '🚙'
        row.mid = mid
        row.vehicle_type_ref = veh_type_ref

        veh_ref = cv.get_rows(search=mid)[0]

        return veh_ref

    def create_camp_route(self, aka):
        camp_ref = self.check_if_ref_exists('camp_route', aka)
        if camp_ref is not None:
            return camp_ref

        cv = self.get_table('camp_route')
        row = cv.add_row()
        row.icon = '🔃'
        row.name = aka
        row.aka = aka

        camp_ref = cv.get_rows(search=aka)[0]
        return camp_ref

    # get latest Detail Name
    def get_latest_detail_index(self):
        index = 0
        maxIndex = 0
        cv = self.get_table('detail_list')
        for row in cv.get_rows():
            index = int(row.title.split(" ")[1])
            if index > maxIndex:
                maxIndex = index
        maxIndex += 1
        return maxIndex

    # for creating blocks recursively
    def append_all_blocks(self, node, template):
        for block in template:
            newNode = node.add_new(block.type, title=block.title)
            if len(block.children) > 0:
                self.append_all_blocks(newNode.children, block.children)

    # create a now boc record for new detail
    def create_boc_record(self, detailIndex):
        boc_template = self.get_template("boc")
        title = "Detail " + str(detailIndex) + "/1"

        cv = self.get_table('boc_record')
        row = cv.add_row()
        row.icon = '☑️'
        row.title = title
        row.status = boc_template.status
        result = cv.get_rows(search=title)[0]

        path = "<REMOVED>" + \
            result.title.replace("/", "-") + "-" + result.id.replace("-", "")
        page = self.client.get_block(path)
        self.append_all_blocks(page.children, boc_template.children)
        return result

    # create actual detail
    def create_detail(self, detail: Detail):
        detail_template = self.get_template("detail")

        cv = self.get_table('detail_list')
        row = cv.add_row()
        row.icon = '🎟️'
        row.title = detail.title
        row.status = detail_template.status
        row.supporting = detail.supporting
        row.purpose = detail.purpose
        row.poc = "[{} ({})](https://wa.me/65{})".format(detail.poc,
                                                         detail.poc_contact, detail.poc_contact)

        row.assigned_vehicle = detail.veh_ref
        row.bOC_record = detail.boc_ref
        row.reporting = detail.reporting_ref
        row.destination = detail.destination_ref
        row.duration = detail.get_duration()

        result = cv.get_rows(search=detail.title)[0]
        return result

    def insert_detail_to_notion(self, source_id, debug=False):
        # get raw input from page body
        source = self.get_body(
            "<REMOVED>{}".format(source_id.replace("-", "")))

        # preprocess source, return: detail object
        my_detail = self.pre_process_detail(source)

        if debug:
            return my_detail

        result = []

        # check if veh mid record exists, else create record, return: veh mid ref
        for detail in my_detail:
            veh_ref = self.create_vehicle_md_type_record(
                detail.mid, detail.veh_type)
            reporting_ref = self.create_camp_route(detail.resporting)
            destination_ref_list = []
            for item in detail.destination:
                destination_ref_list.append(self.create_camp_route(item))

            # create boc record, return boc record ref
            new_detail_index = self.get_latest_detail_index()
            boc_ref = self.create_boc_record(new_detail_index)

            # create detail
            detail.set_title(new_detail_index)
            detail.set_ref(veh_ref, boc_ref, reporting_ref,
                           destination_ref_list)
            detail_ref = self.create_detail(detail)
            result.append(detail_ref)

        return result

    def set_config(self, key, value):
        self.configs[key] = value

    def get_config(self, key):
        return self.configs[key]

    def get_table_ref(self, key):
        return self.client.get_collection_view(self.get_config(key))

    def get_table(self, key):
        return self.get_table_ref(key).collection

    def get_template(self, key):
        return self.client.get_block(self.get_config(key))

    def get_body(self, subject_url):
        body = self.client.get_block(subject_url)
        x = []
        for block in body.children:
            if hasattr(block, 'title') and block.title != "":
                x.append(block.title)
        f = "\n".join(x).replace("_", "").replace("*","")
        return f


def gen_table_row_callback(record, changes):
    if changes[0][0] == "prop_changed":
        start = record.start_task
        record.start_task = False
        if start and record.source != "" and record.status == "Not Started":
            handler.print("Detail generation task starting: " + record.title)
            record.status = "Processing"
            try:
                handler.print("Detail generation task in progress")
                record.result = notion.insert_detail_to_notion(record.id)
                record.status = "Completed"
                handler.print("Detail generation task completed!")
            except Exception as e:
                record.status = "Error"
                handler.error(traceback.format_exc())
        time.sleep(sleep)


def gen_reporting_text(veh_type, mid, avi, fe):
    return "1 x {} moving off from [] to []\nMID : {}\nTO : LCP <REMOVED>\nVC : []\nAVI : {}\nFE : {}\nPurpose : []".format(veh_type, mid, avi, fe)


def boc_collection_row_callback(record, changes):
    if changes[0][0] == "prop_changed" and str(changes[0][2][1]) == "True":
        if record.status != "Not Started" and record.status != "Cancelled":
            if record.avi != "" and record.fe != "" and not record.generate_reporting_text and record.done_on is None:
                if record.status == "Pass":
                    handler.print("Boc status passed, starting sequence...")
                    mid = record.for_detail[0].assigned_vehicle[0].mid
                    veh_type = record.for_detail[0].assigned_vehicle[0].vehicle_type_ref[0].vehicle_type
                    record.for_detail[0].reporting_template = gen_reporting_text(
                        veh_type, mid, record.avi, record.fe)
                    record.generate_reporting_text = True
                    handler.print("Boc status passed, Done")

                record.done_on = NotionDate(datetime.now())
            else:
                if record.status == "Pass" and record.avi == "" and record.fe == "":
                    record.status = "Not Started"
                    handler.print("Boc status invalid action")
        else:
            if record.generate_reporting_text:
                record.generate_reporting_text = False
                handler.print("Boc status invalid action")
        time.sleep(sleep)


def main():
    try:
        handler.print("Detail Task Handler Started")

        handler.print("Registering detail generation task table row callbacks")
        for row in collections["gen_task"].get_rows():
            row.add_callback(gen_table_row_callback,
                             callback_id="gen_table_row_callback")

        handler.print("Registering boc table row callbacks")
        for row in collections["boc"].get_rows():
            row.add_callback(boc_collection_row_callback,
                             callback_id="boc_collection_row_callback")

        handler.print("Ready and listening!")
        while True:
            pass

    except Exception as e:
        handler.error(traceback.format_exc())
    except KeyboardInterrupt as e:
        exit()


def init():
    global handler, notion, collections
    handler = TaskHandler(sys.argv[1])
    handler.configs["detail_local_config"] = "<REMOVED>"
    notion = DetailUtils(handler.configs)

    handler.print("Loading detail local configs")
    for row in notion.get_table("detail_local_config").get_rows():
        if row.name != "":
            notion.set_config(row.name, row.value)

    handler.print("Loading collections")
    collections = {}
    collections["gen_task"] = notion.get_table("detail_gen_task")
    collections["detail"] = notion.get_table("detail_list")
    collections["boc"] = notion.get_table("boc_record")


if __name__ == "__main__":
    init()
    main()
