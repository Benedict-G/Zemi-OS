import caldav
from datetime import datetime, timedelta

CALDAV_URL = "http://127.0.0.1:8080/remote.php/dav"
USERNAME = "zemi"
PASSWORD = "zemicloud2026"

def get_all_calendars():
    client = caldav.DAVClient(
        url=CALDAV_URL,
        username=USERNAME,
        password=PASSWORD
    )
    principal = client.principal()
    return principal.calendars()

def add_event(title, start, duration_hours=1.0, description=""):
    calendars = get_all_calendars()
    cal = calendars[0]
    end = start + timedelta(hours=duration_hours)
    ical = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:" + title + "\nDTSTART:" + start.strftime('%Y%m%dT%H%M%S') + "\nDTEND:" + end.strftime('%Y%m%dT%H%M%S') + "\nDESCRIPTION:" + description + "\nEND:VEVENT\nEND:VCALENDAR"
    cal.add_event(ical)
    return "Event '" + title + "' added on " + start.strftime('%b %d at %I:%M %p')

def list_events(days_ahead=7, date=None):
    calendars = get_all_calendars()
    now = datetime.utcnow()
    if date:
        try:
            start = datetime.strptime(date, '%Y-%m-%d')
            end = start + timedelta(days=1)
        except:
            start = now
            end = now + timedelta(days=days_ahead)
    else:
        start = now
        end = now + timedelta(days=days_ahead)

    result = []
    for cal in calendars:
        try:
            events = cal.date_search(start=start, end=end)
            for e in events:
                vevent = e.vobject_instance.vevent
                dt = vevent.dtstart.value
                if hasattr(dt, 'strftime'):
                    formatted = dt.strftime('%a %b %d at %I:%M %p')
                else:
                    formatted = str(dt)
                result.append(f"- [{cal.name}] {vevent.summary.value}: {formatted}")
        except:
            pass

    if not result:
        return "No upcoming events found."
    return "\n".join(sorted(result))

if __name__ == "__main__":
    print("Testing calendar...")
    print(list_events())
