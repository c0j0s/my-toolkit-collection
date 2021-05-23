import os
import traceback
from icalendar import Calendar, Event
from flask import make_response
from notion.client import NotionClient
from datetime import datetime, timedelta
from notion_ics import get_ical

def service_handler(request):
    """
    v0.01
    """
    try:
        calendar_url = "<REMOVED>"
        title_format = r"{NAME} - {Status}"
        token = os.environ.get('token')
        client = NotionClient(token, monitor=False)

        event_properties = {'X-MICROSOFT-CDO-BUSYSTATUS':'BUSY'}

        cal = get_ical(client, calendar_url, title_format, **event_properties)
        text = cal.to_ical()
    except Exception as e:
        traceback.print_exc()
        # put it in calendar
        cal = Calendar()
        cal.add("summary", "Imported from Notion, via notion-export-ics, but failed.")
        cal.add('version', '2.0')
        for i in range(7):
            event = Event()
            event.add('dtstart', datetime.now().date() + timedelta(days=i))
            event.add('summary', repr(e))
            cal.add_component(event)
        text = cal.to_ical()
    
    res = make_response(text.decode("utf-8"))
    res.headers.set('Content-Disposition', 'attachment;filename=calendar.ics')
    res.headers.set('Content-Type', 'text/calendar;charset=utf-8')
    return res
