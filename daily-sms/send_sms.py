"""Text CJ today's content-calendar tasks via Twilio.

Runs daily from GitHub Actions. Looks up today's tasks in schedule.json
(exact date first, weekday fallback second) and sends one SMS.
"""

import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SCHEDULE = Path(__file__).parent / "schedule.json"


def todays_tasks() -> tuple[str, list[str]]:
    now = datetime.now(ZoneInfo("America/Phoenix"))
    schedule = json.loads(SCHEDULE.read_text())
    date_key = now.strftime("%Y-%m-%d")
    weekday = now.strftime("%A")
    tasks = schedule["dates"].get(date_key) or schedule["fallback"].get(weekday.lower(), [])
    return weekday, tasks


def build_message(weekday: str, tasks: list[str]) -> str:
    lines = [f"CJ CONTENT - {weekday.upper()}"]
    lines += [f"- {t}" for t in tasks]
    if any("Post" in t for t in tasks):
        lines.append("Reply to every comment in the first hour!")
    lines.append("Scripts + captions are in our Claude chat. Go get it.")
    return "\n".join(lines)


def build_week_message() -> str:
    schedule = json.loads(SCHEDULE.read_text())
    lines = [f"CJ CONTENT WEEK ({schedule.get('week_label', '')})"]
    for date_key in sorted(schedule["dates"]):
        day = datetime.strptime(date_key, "%Y-%m-%d").strftime("%a %b %d").upper()
        lines.append(f"\n{day}:")
        lines += [f"- {t}" for t in schedule["dates"][date_key]]
    lines.append("\nDaily detail text arrives 7am each morning. Scripts in Claude chat.")
    return "\n".join(lines)


def send_sms(body: str) -> None:
    sid = os.environ["TWILIO_ACCOUNT_SID"]
    token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ["TWILIO_FROM_NUMBER"]
    to_number = os.environ["MY_PHONE_NUMBER"]

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data = urllib.parse.urlencode(
        {"From": from_number, "To": to_number, "Body": body}
    ).encode()
    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    request = urllib.request.Request(
        url, data=data, headers={"Authorization": f"Basic {auth}"}
    )
    with urllib.request.urlopen(request, timeout=30) as resp:
        result = json.loads(resp.read())
    print(f"Sent: sid={result.get('sid')} status={result.get('status')}")


def main() -> int:
    if "--week" in sys.argv:
        message = build_week_message()
    else:
        weekday, tasks = todays_tasks()
        if not tasks:
            print(f"No tasks for {weekday}; not sending.")
            return 0
        message = build_message(weekday, tasks)
    print(f"Message ({len(message)} chars):\n{message}\n")
    if "--dry-run" in sys.argv:
        print("Dry run: not sending.")
        return 0
    send_sms(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
