from detail import Detail
from notion_handler import NotionHandler
from icalendar import *
import re
from functools import reduce
import datetime
import requests, time

class NotionController:
    """
    For front-end layer to request feature related functions
    v0.07
    """

    def __init__(self, token, debug=False):
        self.debug = debug
        self.handler = NotionHandler(token, debug)

    def split_text_to_detail_list(self, source: str = "") -> list:
        """
        Converts text into an array of detail array.
        source: raw text input
        """
        assert source != "", "Source cannot be empty"

        # Remove whatsapp bold
        source = source.replace("*", "")

        # Split into lines
        source = source.split("\n")

        # Split Into Days
        detail_text_in_days = []
        detail_per_day = []

        allow_entry = False

        # Split detail text into days
        # ============================
        for line in source:
            line = line.replace("\r", "").replace("\n", "")

            if re.search("^_*", line)[0] != "":
                detail_text_in_days.append(detail_per_day[:])
                detail_per_day.clear()
            else:
                # Throw empty line
                if line != "":
                    detail_per_day.append(line)

        # Add last entry is exist
        if len(detail_per_day) > 0:
            detail_text_in_days.append(detail_per_day[:])

        # Split detail text into individual detail array
        # ============================
        detail_list = []

        for item in detail_text_in_days:
            if len(item) > 1:
                detail = []
                for line in item:
                    if re.search(r"^[0-9]{2}$", line) is not None:
                        allow_entry = True
                        continue

                    if allow_entry:
                        detail.append(line)

                    if line.startswith("POC"):
                        allow_entry = False
                        detail_list.append(detail[:])
                        detail.clear()

        if self.debug:
            print("[split_text_to_detail_list] {}".format(
                str(len(detail_list))))

        return detail_list

    def text_to_json_detail_list(self, data) -> list:
        try:
            detail_list = self.split_text_to_detail_list(data)
            person_detail = []

            for item in detail_list:
                d = Detail()
                d.build_detail_objects_from_list(item, debug=self.debug)
                if d.is_subject:
                    person_detail.append(d)

                    if self.debug:
                        print(d.to_json())
            
            return person_detail
        except Exception as e:
            return "[text_to_detail_json] " + str(e)

    def write_detail_json_to_notion(self, data):
        detail = Detail(**data)
        return self.write_detail_object_to_notion(detail)

    def write_detail_object_to_notion(self, d: Detail):
        try:
            detail_index = self.handler.get_latest_detail_index() + 1

            assert d is not None, "Invalid detail data!"

            if self.debug:
                print("[write_detail_object_to_notion] {}".format(d.mid))

            d.title = "Detail {}".format(detail_index)
            d.duration = self.handler.to_notion_duration(
                d.start_date, d.start_time, d.end_date, d.end_time)

            d.veh_ref = self.handler.if_ref_exists(
                self.handler.notion_table["veh_type_mid"], d.mid)
            if d.veh_ref is False:
                d.veh_ref = self.handler.create_vehicle_mid_type_record(
                    d.mid, d.veh_type)

            d.reporting_ref = self.handler.if_ref_exists(
                self.handler.notion_table["camp_route"], d.reporting)
            if d.reporting_ref is False:
                d.reporting_ref = self.handler.create_camp_route(d.reporting)

            d.destination_ref = self.handler.if_ref_exists(
                self.handler.notion_table["camp_route"], d.destination)
            if d.destination_ref is False:
                d.destination_ref = self.handler.create_camp_route(d.destination)

            # d.boc_ref = self.handler.create_boc_record(detail_index)

            result = self.handler.create_detail(d)

            return result
        except Exception as e:
            return "[write_detail_object_to_notion] " + str(e)

    def get_ns_events(self) -> str:
        """
        Compile both detail and admin schedule, return list of events
        """

        cal = Calendar()
        cal.add('prodid', '-//Export from Notion//EN')
        cal.add('version', '2.0')
        cal.add('TZID', 'Malay Peninsula Standard Time')

        # get detail tasking
        cv = self.handler.client.get_collection_view(
            self.handler.notion_table["detail_list"])

        for item in cv.collection.get_rows():
            try:
                print(item)
                event = Event()
                event.add('UID', item.id)

                title = "{} - {}".format(item.purpose, item.status)
                event.add('SUMMARY', title)
                # description = "Supporting {} for {}.\n".format(
                #     item.supporting, item.purpose)
                description = "- Vehicle: MID{} {}\n".format(
                    item.assigned_vehicle[0].mid, item.assigned_vehicle[0].vehicle_type_ref[0].title)
                description += "- Reporting venue: {}\n".format(
                    item.reporting[0].title)
                description += "- Exercise venue: {}\n".format(
                    item.destination[0].title)

                if "](" in item.poc:
                    poc = item.poc.split("](")
                    description += "- POC: {}\r\n".format(
                        "{} <{}>".format(poc[0].replace("[", ""), poc[1].replace(")", "")))
                else:
                    poc = item.poc

                start, end = self.__notion_date_to_ical__(
                    item.duration.start, item.duration.end)
                event.add('DTSTART', start)
                if end is not None:
                    event.add('DTEND', end)

                event.add('LOCATION', item.destination[0].title)
                event.add('X-MICROSOFT-CDO-BUSYSTATUS', "BUSY")
                event.add('DESCRIPTION', description)
                cal.add_component(event)
            except Exception as e:
                # skip item with invalid fields
                print("get_ns_events - details: " + str(e))

        # get admin schedule
        cv = self.handler.client.get_collection_view(
            self.handler.notion_table["admin_schedule"])

        for item in cv.collection.get_rows():
            try:
                event = Event()
                event.add('UID', item.id)

                title = "{}".format(item.title)
                event.add('SUMMARY', title)

                if self.debug:
                    print("Creating event: {}".format(title))

                start, end = self.__notion_date_to_ical__(
                    item.duration.start, item.duration.end)
                event.add('DTSTART', start)
                if end is not None:
                    event.add('DTEND', end)

                if len(item.Location) > 0:
                    event.add('LOCATION', item.Location[0].title)

                if item.activity_type == "Off" or item.activity_type == "Leave":
                    event.add('X-MICROSOFT-CDO-BUSYSTATUS', "FREE")
                else:
                    event.add('X-MICROSOFT-CDO-BUSYSTATUS', "BUSY")

                if len(item.children) > 0:
                    desc = reduce(lambda x, y: "{} \n{}".format(
                        x, y), map(lambda x: x.title, item.children))
                    event.add('DESCRIPTION', desc)

                cal.add_component(event)
            except Exception as e:
                # skip item with invalid fields
                print("get_ns_events - admin: " + str(e))

        if self.debug:
            print("[get_ns_events]")
            print(cal.to_ical().decode("utf-8"))

        return cal.to_ical().decode("utf-8")

    def __notion_date_to_ical__(self, start, end=None):
        """
        Add end date for event without time specified
        """
        # whole day event
        if end is not None and not isinstance(end, datetime.datetime):
            end += datetime.timedelta(days=(1))
        
        # hour event
        if end is None:
            end = start + datetime.timedelta(hours=(1))

        return start, end

    def get_shark_rooms(self, watchlist=[]):
        """
        Get room infos from shark apis
        """

        endpoint = "http://open.douyucdn.cn/api/RoomApi/room/{}"
        external = "https://www.douyu.com/{}"
        rooms=[]

        if len(watchlist) > 0:
            for i in watchlist:
                try:
                    r = requests.get(endpoint.format(str(i))).json()
                    room_data = r["data"]
                    del room_data["gift"]
                    room_data["redirect"] = external.format(str(i))
                    rooms.append(room_data)
                    time.sleep(1)
                except Exception as e:
                    print(e)
        rooms = sorted(rooms, key=lambda k: k['online'], reverse=True) 
        
        return rooms