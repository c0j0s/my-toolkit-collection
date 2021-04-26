import os
from notion_controller import NotionController
import json


def service_handler(request):
    """
    v0.03
    """
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    result=None

    try:
        request_json = request.get_json()
        controller = NotionController(os.environ.get('token'), debug=True)

        if controller.debug:
            print("request received: " + json.dumps(request_json, sort_keys=True, indent=4, ensure_ascii=False))

        if request_json and 'method' in request_json and 'token' in request_json:
            """
            Requests required token verification
            """

            assert request_json["token"] == os.environ.get('token')
            assert "payload" in request_json

            method = str(request_json["method"])
            payload = request_json["payload"]
            
            if method == "detail_text_to_detail_json":
                # text -> detail object -> detail json
                details = controller.text_to_json_detail_list(payload)

                result = json.dumps(list(map(lambda x: x.__dict__, details)))

            elif method == "detail_write_detail_json_to_notion":
                # detail json -> detail object -> write to notion
                result = json.dumps(list(map(lambda x: str(controller.write_detail_json_to_notion(x)), payload)))

            elif method == "detail_text_to_notion":
                # text -> detail object -> write to notion
                details = controller.text_to_json_detail_list(payload)
                result = json.dumps(list(map(lambda x: str(controller.write_detail_object_to_notion(x)), details)))
            
            return (result, 200, headers)

        elif 'method' in request_json:
            """
            Requests without token verification
            """

            assert "payload" in request_json

            method = str(request_json["method"])
            payload = request_json["payload"]

            if method == "get_shark_rooms":
                rooms = controller.get_shark_rooms(payload)
                result = json.dumps(rooms, ensure_ascii=False)
                headers['Content-Type'] = 'application/json;charset=utf-8'
            
            return (result, 200, headers)
        else:
            """
            Fallback requests without token verification and specified methods
            """

            result = controller.get_ns_events()
            headers['Content-Type'] = 'text/calendar;charset=utf-8'
            headers['Content-Disposition'] = 'attachment;filename=calendar.ics'
            return (result, 200, headers)

    except Exception as e:
        print("notion_handler: " + str(e))

    return f'Invalid Response! your entry information will be logged and tracked.'
