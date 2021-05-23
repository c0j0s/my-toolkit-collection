from notion.client import NotionClient
from notion.collection  import NotionDate
from notionUtils import Detail
import json
import re
from datetime import datetime

notion_pages = {
    "detail_list":"<REMOVED>",
    "boc_record":"<REMOVED>",
    "veh_types":"<REMOVED>",
    "veh_type_mid":"<REMOVED>",
    "camp_route":"<REMOVED>"
}

notion_templates = {
    "veh_mid_type":"<REMOVED>",
    "boc" : "<REMOVED>"
}

token_v2 = "<REMOVED>"

client = NotionClient(token_v2=token_v2,monitor=False)


# create actual detail
def create_detail(detail:Detail):
    print(detail)

    cv = client.get_collection_view(notion_pages['detail_list'])
    row = cv.collection.add_row()
    row.title = "testing"
    row.duration = detail.get_duration()

    result = cv.default_query().execute()

x = Detail()
x.buildFromSource(["24/06/20 0500hrs to 24/06/20 1030hrs"])
create_detail(x)