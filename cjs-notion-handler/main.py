import os
from detail import *
from notion_handler import NotionHandler
from icalendar import *
from flask import make_response

def notion_handler(request):
    try:
        request_json = request.get_json()
        if request_json and 'token' in request_json and 'method' in request_json:
            assert request_json["token"] == os.environ.get('token')
            assert "payload" in request_json

            method = request_json["method"]
            payload = request_json["payload"]
            if method == "text_to_detail_json":
                detail = text_to_detail_json(payload)
                return detail.to_json()

            elif method == "write_detail_object_to_notion":
                return write_detail_object_to_notion(payload)

            elif method == "detail_text_to_notion":
                detail = text_to_detail_json(payload)
                return str(write_detail_object_to_notion(detail.__dict__))
            
        else:
            data = get_detail_calandar()
            resp = make_response(data)
            resp.headers.set('Content-Disposition', 'attachment;filename=calendar.ics')
            resp.headers.set('Content-Type', 'text/calendar;charset=utf-8')
            return resp

    except Exception as e:
        print("notion_handler: " + str(e))
    
    return f'Invalid Response! your entry information will be logged and tracked.'


def text_to_detail_json(payload):
    try:
        detail_list = text_to_detail_list(payload)
        for item in detail_list:
            d = Detail()
            d.build_detail_objects_from_list(item,debug=False)
            if d.is_subject:
                return d
    except Exception as e:
        return "text_to_detail_json: " + str(e)

def write_detail_object_to_notion(payload):
    try:
        debug = False

        # Convert dict to detail object
        handler = NotionHandler(os.environ.get('token'),debug)
        detail_index = handler.get_latest_detail_index() + 1

        d = Detail(**payload)
        d.title = "Detail {}".format(detail_index)
        d.duration = handler.to_notion_duration(d.start_date,d.start_time,d.end_date,d.end_time)
        
        d.veh_ref = handler.if_ref_exists(handler.notion_table["veh_type_mid"], d.mid)
        if d.veh_ref is False:
            d.veh_ref = handler.create_vehicle_mid_type_record(d.mid,d.veh_type)
        
        d.reporting_ref = handler.if_ref_exists(handler.notion_table["camp_route"], d.reporting)
        if d.reporting_ref is False:
            d.reporting_ref = handler.create_camp_route(d.reporting)
        
        d.destination_ref = handler.if_ref_exists(handler.notion_table["camp_route"], d.destination)
        if d.destination_ref is False:
            d.destination_ref = handler.create_camp_route(d.reporting)
        
        d.boc_ref = handler.create_boc_record(detail_index)

        result = handler.create_detail(d)
        
        return result
    except Exception as e:
        return "write_detail_object_to_notion: " + str(e)

def get_detail_calandar():
    handler = NotionHandler(os.environ.get('token'))
    return handler.get_ns_events()