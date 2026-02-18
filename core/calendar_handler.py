import caldav
from datetime import datetime, timedelta

CALDAV_URL = "http://127.0.0.1:8080/remote.php/dav"
USERNAME = "zemi"
PASSWORD = "zemicloud2026"

def get_calendar():
    client = caldav.DAVClient(
        url=CALDAV_URL,
        username=USERNAME,
        password=PASSWORD
    )
    principal = client.principal()
    calendars = principal.calendars()
    return calendars[0]

def add_event(title, start, duration_hours=1.0, description=""):
    cal = get_calendar()
    end = start + timedelta(hours=duration_hours)
    ical = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:" + title + "\nDTSTART:" + start.strftime('%Y%m%dT%H%M%S') + "\nDTEND:" + end.strftime('%Y%m%dT%H%M%S') + "\nDESCRIPTION:" + description + "\nEND:VEVENT\nEND:VCALENDAR"
    cal.add_event(ical)
    return "Event '" + title + "' added on " + start.strftime('%b %d at %I:%M %p')

def list_events(days_ahead=7):
    cal = get_calendar()
    now = datetime.utcnow()
    end = now + timedelta(days=days_ahead)
    events = cal.date_search(start=now, end=end)
    if not events:
        return "No upcoming events found."
    result = []
    for e in events:
        vevent = e.vobject_instance.vevent
        result.append("- " + vevent.summary.value + ": " + str(vevent.dtstart.value))
    return "\n".join(result)

if __name__ == "__main__":
    print("Testing calendar...")
    tomorrow = datetime.now() + timedelta(days=1)
    test_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    print(add_event("Zemi Calendar Live!", test_time))
    print(list_events())
