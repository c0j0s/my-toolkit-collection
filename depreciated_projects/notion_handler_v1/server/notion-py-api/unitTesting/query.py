# from notion.client import NotionClient
from notion.client import NotionClient
notion_pages = {
    "detail_list":"<REMOVED>",
    "boc_record":"<REMOVED>",
    "veh_types":"<REMOVED>",
    "veh_type_mid":"<REMOVED>",
    "camp_route":"<REMOVED>"
}

token_v2 = "<REMOVED>"

client = NotionClient(token_v2=token_v2,monitor=False)

filter_params = [{
    "property": "mid",
    "filter": {
    "operator": "string_contains",
    "value": {
        "type": "exact",
        "value": "34131"
    }
    }
}]
cv = client.get_collection_view(notion_pages['veh_type_mid'])
result = cv.collection.get_rows(search="34131")
print(result)