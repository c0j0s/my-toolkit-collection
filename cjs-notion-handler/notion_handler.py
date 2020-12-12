from notion.client import NotionClient
from notion.collection import NotionDate
from notion.collection import CollectionRowBlock
from datetime import datetime
from detail import Detail
from icalendar import *
from functools import reduce

class NotionHandler:
    notion_table = {}
    notion_table["veh_types"] = "https://www.notion.so/c0j0s/d27519769c07444c87a3165ac53e1f50?v=50126105371e4e959b60879354f3379d"
    notion_table["veh_type_mid"] = "https://www.notion.so/c0j0s/603ea7ccad2847b4a5335ade8ffb7b08?v=7d647975956e49b896285ba8b133c15a"
    notion_table["camp_route"] = "https://www.notion.so/c0j0s/d8d88e11c1a64fd7bd5047c4fe3ae999?v=cde456130b0948e79882709c6763e4be"
    notion_table["detail_list"] = "https://www.notion.so/c0j0s/42c45fe6aad64a719ac83d6dd52690a2?v=6fbbce6798f545329e6a9b0932b8367b"
    notion_table["boc_record"] = "https://www.notion.so/c0j0s/5b319f55357e4c7fbac4ca863addb852?v=5b5aee2bd48d4b6b970f056d02984a82"
    notion_table["admin_schedule"] = "https://www.notion.so/c0j0s/2f422a7ee01e4c69be1df1746e187fbf?v=21393046f06e43dda4cf4c21612a8241"
    
    def __init__(self, token, debug=False):
        self.client = NotionClient(token_v2=token)
        self.debug = debug

    """
    Helper functions
    """

    def if_ref_exists(self, table, keyword):
        """
        Check if a record exisits in notion.
        Return a result if exisits, else False.
        """
        result = self.client.get_collection_view(table).collection.get_rows(search=keyword)
        if len(result) > 0:
            
            if self.debug:
                print("[if_ref_exists]")
                print(result[0])
                print("-")

            return result[0]
        return False
    
    def get_latest_detail_index(self) -> int:
        """
        Get the latest detail index from notion
        """

        sort_params = [{
            "direction": "descending",
            "property": "name",
        }]
        cv = self.client.get_collection_view(self.notion_table['detail_list'])
        result = int(cv.build_query(sort=sort_params).execute()[0].title.split(" ")[1])
        
        assert isinstance(result,int), "Invalid detail index."
        
        if self.debug:
            print("[get_latest_detail_index]")
            print(result)
            print("-")

        return result

    def to_notion_duration(self,sd,st,ed,et):
        """
        Converts datetime string into NotionDate object.
        """

        date_format = '%d/%m/%y %H%M'
        start_datetime = sd + " " + st
        end_datetime = ed + " " + et
        duration_start = datetime.strptime(start_datetime, date_format)
        duration_end = datetime.strptime(end_datetime, date_format)
        timezone = "Asia/Singapore"
        return NotionDate(duration_start, duration_end, timezone)

    """
    Create Record Methods
    """
    def create_vehicle_mid_type_record(self, mid, veh_type):
        """
        create a new vehicle mid record: 
        param : mid, veh_type
        return : ref
        """

        # check if vehicle type is valid
        veh_type_ref = self.if_ref_exists(self.notion_table['veh_types'], veh_type)
        assert veh_type_ref, "Unknown Vehicle Type"

        cv = self.client.get_collection_view(self.notion_table['veh_type_mid'])
        row = cv.collection.add_row()
        row.icon = '🚙'
        row.mid = mid
        row.vehicle_type_ref = veh_type_ref

        if self.debug:
            print("[create_vehicle_mid_type_record]")
            print(veh_type_ref)
            print("-")

        return row

    def create_camp_route(self, aka):
        """
        create camp route record
        """
        cv = self.client.get_collection_view(self.notion_table['camp_route'])
        row = cv.collection.add_row()
        row.icon = '🔃'
        row.name = aka
        row.aka = aka

        if self.debug:
            print("[create_camp_route]")
            print(row)
            print("-")

        return row

        
    def create_boc_record(self, detail_index):
        """
        create a new boc record for new detail
        """

        cv = self.client.get_collection_view(self.notion_table['boc_record'])
        row = cv.collection.add_row()
        row.icon = '☑️'
        row.title = "Detail " + str(detail_index) + "/1"
        row.status = "Not Started"

        if self.debug:
            print("[create_boc_record]")
            print(row)
            print("-")

        return row

    def create_detail(self, detail: Detail):
        """
        create a new detail
        """

        cv = self.client.get_collection_view(self.notion_table['detail_list'])
        row = cv.collection.add_row()
        row.icon = '🎟️'
        row.title = detail.title
        row.status = "Upcoming"
        row.supporting = detail.supporting
        row.purpose = detail.purpose
        row.poc = "[{} ({})](https://wa.me/65{})".format(detail.poc,
                                                         detail.poc_contact, detail.poc_contact)

        row.assigned_vehicle = detail.veh_ref
        row.bOC_record = detail.boc_ref
        row.reporting = detail.reporting_ref
        row.destination = detail.destination_ref
        row.duration = detail.duration

        if self.debug:
            print("[create_detail]")
            print(row)
            print("-")
        return row

    def get_ns_events(self):
        """
        Compile both detail and admin schedule, return list of events
        """

        cal = Calendar()
        cal.add('prodid', '-//Export from Notion//EN')
        cal.add('version', '2.0')
        cal.add('TZID', 'Malay Peninsula Standard Time')

        # get detail tasking 
        cv = self.client.get_collection_view(self.notion_table["detail_list"])

        for item in cv.collection.get_rows():
            event = Event()
            event.add('UID',item.id)

            title = "[{}] - {}".format(item.status, item.purpose)
            event.add('SUMMARY', title)
            description = "Supporting {} for {}.\n".format(item.supporting, item.purpose)
            description += "- Vehicle           : MID{} {}\n".format(item.assigned_vehicle[0].mid, item.assigned_vehicle[0].vehicle_type_ref[0].title)
            description += "- Reporting venue   : {}\n".format(item.reporting[0].title)
            description += "- Exercise venue    : {}\n".format(item.destination[0].title)

            poc = item.poc.split("](")
            description += "- POC               : {}\r\n".format("{} <{}>".format(poc[0].replace("[",""),poc[1].replace(")","")))

            event.add('DTSTART', item.duration.start)
            event.add('DTEND', item.duration.end)
            event.add('LOCATION',item.destination[0].title)
            event.add('X-MICROSOFT-CDO-BUSYSTATUS',"BUSY")
            event.add('CN', 'c0j0s@hotmail.com')
            event.add('DESCRIPTION', description)
            cal.add_component(event)
            
        # get admin schedule
        cv = self.client.get_collection_view(self.notion_table["admin_schedule"])

        for item in cv.collection.get_rows():
            event = Event()
            event.add('UID',item.id)

            title = "[{}] - {}".format(item.activity_type, item.title)
            event.add('SUMMARY', title)
            event.add('DTSTART', item.duration.start)

            if item.duration.end is not None:
                event.add('DTEND', item.duration.end)

            if len(item.Location) > 0:
                event.add('LOCATION',item.Location[0].title)

            if item.activity_type == "Off" or item.activity_type == "Leave":
                event.add('X-MICROSOFT-CDO-BUSYSTATUS',"FREE")
            else:
                event.add('X-MICROSOFT-CDO-BUSYSTATUS',"BUSY")

            event.add('CN', 'c0j0s@hotmail.com')

            if len(item.children) > 0:
                desc = reduce(lambda x, y: "{} \n{}".format(x,y), map(lambda x: x.title, item.children))
                event.add('DESCRIPTION', desc)

            cal.add_component(event)

        if self.debug:
            print("[get_ns_events]")
            print(cal.to_ical().decode("utf-8"))

        return cal.to_ical().decode("utf-8")
