# from notion.client import NotionClient
from notion.client import NotionClient
notion_pages = {
    "detail_list":"https://www.notion.so/c0j0s/42c45fe6aad64a719ac83d6dd52690a2?v=6fbbce6798f545329e6a9b0932b8367b",
    "boc_record":"https://www.notion.so/c0j0s/5b319f55357e4c7fbac4ca863addb852?v=5b5aee2bd48d4b6b970f056d02984a82",
    "veh_types":"https://www.notion.so/c0j0s/d27519769c07444c87a3165ac53e1f50?v=50126105371e4e959b60879354f3379d",
    "veh_type_mid":"https://www.notion.so/c0j0s/603ea7ccad2847b4a5335ade8ffb7b08?v=7d647975956e49b896285ba8b133c15a",
    "camp_route":"https://www.notion.so/c0j0s/d8d88e11c1a64fd7bd5047c4fe3ae999?v=cde456130b0948e79882709c6763e4be"
}

token_v2 = "ac03018c7b94a27f3a5361a207255deb1cdc83e840f5895c5f6382dd97890de1aba1d3a9bb7889493702e571caa90803b4ba85a5899118a60cab111754cc073dca0ef548317e034041b96e538f37"

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