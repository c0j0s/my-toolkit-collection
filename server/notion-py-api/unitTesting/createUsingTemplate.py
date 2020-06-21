from notion.client import NotionClient
from notion.block import *
from flask import Flask

notion_pages = {}

notion_templates = {}

token_v2 = ""

client = NotionClient(token_v2=token_v2,monitor=False)

def getTemplate(path):
    page = client.get_block(path)
    print(page.status)
    return page.children

def createVehicleMidRecord(mid,veh_type,template):
    # get veh type ref
    typeRef = None
    cv_veh_type = client.get_collection_view(notion_pages['veh_types'])
    for row in cv_veh_type.collection.get_rows(search=veh_type):
        print(row.title)
        if str(row.title) == veh_type:
            typeRef = row
    print(typeRef)
    # create new record: title:mid, type:ref
    cv_mid_record = client.get_collection_view(notion_pages['veh_type_mid'])
    row = cv_mid_record.collection.add_row()
    row.mid = mid
    row.vehicle_type_ref = typeRef
    result = cv_mid_record.default_query().execute()
    for row in result:
        if row.mid == mid:
            path = "https://www.notion.so/c0j0s/" + mid + "-" + row.id.replace("-","")
            page = client.get_block(path)
            appendAllBlocks(page.children,template)
            return page

def appendAllBlocks(node,content):
    for block in content:
        newNode = node.add_new(block.type,title=block.title)
        print(block)

        if len(block.children) > 0:
            appendAllBlocks(newNode.children,block.children)
            
def getLatestDetailName():
    title = ""
    index = 0
    maxIndex = 0
    cv = client.get_collection_view(notion_pages['detail_list'])
    for row in cv.collection.get_rows():
        index = int(row.title.split(" ")[1])
        if index > maxIndex:
            title = row.title
            maxIndex = index
    return maxIndex

def getDate():
    cv = client.get_collection_view(notion_pages['detail_list'])
    for row in cv.collection.get_rows():
        print(row.duration.)

# createVehicleMidRecord("MID11302","SOUV",getTemplate(notion_templates["boc"]))
# print(getTemplate(notion_templates["boc"]))
# print(getLatestDetailName())
getDate()