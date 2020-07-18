from notion.client import NotionClient
from flask import Flask

def createVehicleMidRecord(mid,veh_type):
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
        print(row)
    return ""

createVehicleMidRecord("MID111","SOUV")