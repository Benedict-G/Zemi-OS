import caldav
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os

def load_bridge_password():
    vault_dir = os.path.expanduser("~/ZemiV1/vault")
    with open(f"{vault_dir}/master.key", "rb") as f:
        key = f.read()
    fernet = Fernet(key)
    with open(f"{vault_dir}/proton.enc", "rb") as f:
        return fernet.decrypt(f.read()).decode()

def get_calendar():
    password = load_bridge_password()
    client = caldav.DAVClient(
        url="https://calendar.proton.me/dav",
        username="guadalupe.anthony@protonmail.com",
        password=password
    )
    principal = client.principal()
    calendars = principal.calendars()
    return calendars[0]

def add_event(title: str, start: datetime, duration_hours: float = 1.0, description: str = ""):
    cal = get_calendar()
    end = start + timedelta(hours=duration_hours)
    ical = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{title}
DTSTART:{start.strftime('%Y%m%dT%H%M%S')}
DTEND:{end.strftime('%Y%m%dT%H%M%S')}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR"""
    cal.add_event(ical)
    return f"✅ Event '{title}' added on {start.strftime('%b %d at %I:%M %p')}"

def list_events(days_ahead: int = 7):
    cal = get_calendar()
    now = datetime.utcnow()
    end = now + timedelta(days=days_ahead)
    events = cal.date_search(start=now, end=end)
    if not events:
        return "📅 No upcoming events found."
    result = []
    for e in events:
        vevent = e.vobject_instance.vevent
        result.append(f"• {vevent.summary.value} — {vevent.dtstart.value}")
    return "\n".join(result)

if __name__ == "__main__":
    print("Testing calendar connection...")
    tomorrow = datetime.now() + timedelta(days=1)
    test_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    result = add_event("Zemi V1.1 Complete!", test_time, description="Email + Calendar working!")
    print(result)
    print("\nUpcoming events:")
    print(list_events())
