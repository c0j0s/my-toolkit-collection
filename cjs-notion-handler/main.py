import os

from flask import make_response
from notion_controller import NotionController
import json

def notion_handler(request):
    """
    v0.01
    """
    try:
        request_json = request.get_json()
        controller = NotionController(os.environ.get('token'))

        if request_json and 'method' in request_json and 'token' in request_json:
            assert request_json["token"] == os.environ.get('token')
            assert "payload" in request_json

            method = str(request_json["method"])
            payload = request_json["payload"]

            if method == "detail_text_to_detail_json":
                # text -> detail object -> detail json
                details = controller.text_to_json_detail_list(payload)
                
                return json.dumps(list(map(lambda x: x.__dict__, details)))

            elif method == "detail_write_detail_json_to_notion":
                # detail json -> detail object -> write to notion 
                return json.dumps(list(map(lambda x: str(controller.write_detail_json_to_notion(x)), payload)))

            elif method == "detail_text_to_notion":
                # text -> detail object -> write to notion 
                details = controller.text_to_json_detail_list(payload)
                return json.dumps(list(map(lambda x: str(controller.write_detail_object_to_notion(x)), details)))

        else:
            data = controller.get_ns_events()
            resp = make_response(data)
            resp.headers.set('Content-Disposition', 'attachment;filename=calendar.ics')
            resp.headers.set('Content-Type', 'text/calendar;charset=utf-8')
            return resp

    except Exception as e:
        print("notion_handler: " + str(e))
    
    return f'Invalid Response! your entry information will be logged and tracked.'

