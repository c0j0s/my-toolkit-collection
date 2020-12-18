import os
from icalendar import *
from flask import make_response
from notion.client import NotionClient
import datetime

def service_handler(request):
    try:
        """
        v0.01
        """
        request_json = request.get_json()
        
        data = get_calandar(os.environ.get('token'))
        resp = make_response(data)
        resp.headers.set('Content-Disposition', 'attachment;filename=calendar.ics')
        resp.headers.set('Content-Type', 'text/calendar;charset=utf-8')
        return resp

    except Exception as e:
        print("service_handler: " + str(e))
    
    return f'Invalid Response! your entry information will be logged and tracked.'

def get_calandar(token):
    table = "https://www.notion.so/c0j0s/fc9f28f6271c42b0abffe32a2f70cb6b?v=22d66a9ee6b648e78d7a22cdc2741237"

    client = NotionClient(token_v2=token)
    cv = client.get_collection_view(table).collection

    cal = Calendar()    
    cal.add('prodid', '-//Export from Notion//EN')
    cal.add('version', '2.0')
    cal.add('TZID', 'Malay Peninsula Standard Time')

    series_event = []

    for item in cv.get_rows():
        if item.release_date is not None:
            event = Event()
            event.add('UID',item.id)
            event.add('X-MICROSOFT-CDO-BUSYSTATUS',"FREE")
            event.add('CN', 'c0j0s@hotmail.com')
            event.add('DTSTART', item.release_date.start)

            title = "[{}] {} ".format(item.media_type, item.title)
            if item.media_type == "TV" and item.status.lower() == "following" and item.episodes is not None:
                series_event.append(item)
                continue
            
            event.add('SUMMARY', title)

            if item.follow_online != "":
                event.add('DESCRIPTION', item.follow_online)

            cal.add_component(event)

    for item in series_event:
            for i in range(item.episodes):
                event = Event()
                event.add('UID',item.id + str(i))
                event.add('X-MICROSOFT-CDO-BUSYSTATUS',"FREE")
                event.add('CN', 'c0j0s@hotmail.com')

                next_episode = item.release_date.start + datetime.timedelta(days=(7 * i))
                event.add('DTSTART', next_episode)

                title = "[{}] {} Ep{}".format(item.media_type, item.title, str(i + 1))
                event.add('SUMMARY', title)

                if item.follow_online != "":
                    event.add('DESCRIPTION', item.follow_online)
                cal.add_component(event)

    return cal.to_ical().decode("utf-8")