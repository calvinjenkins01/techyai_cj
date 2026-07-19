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


def _emoji(task: str) -> str:
    lowered = task.lower()
    if "film" in lowered:
        return "🎬"
    if "carousel" in lowered:
        return "📸"
    if "x article" in lowered:
        return "🐦"
    if "video" in lowered:
        return "🎥"
    if "planning" in lowered:
        return "🧠"
    return "✅"


def _task_line(task) -> str:
    return task if isinstance(task, str) else task["line"]


def _render_task(task) -> list[str]:
    line = _task_line(task)
    lines = [f"{_emoji(line)} {line}"]
    if isinstance(task, dict):
        if task.get("hook"):
            lines.append(f"🗣 Hook: \"{task['hook']}\"")
        if task.get("caption"):
            lines.append(f"📝 {task['caption']}")
        if task.get("caption_ig"):
            lines.append(f"📷 IG: {task['caption_ig']}")
        if task.get("tip"):
            lines.append(f"💡 {task['tip']}")
    return lines


def build_message(weekday: str, tasks: list) -> str:
    lines = [f"🔥 CJ CONTENT — {weekday.upper()} 🔥"]
    for task in tasks:
        lines.append("")
        lines += _render_task(task)
    lines.append("")
    if any("Post" in _task_line(t) for t in tasks):
        lines.append("💬 Reply to every comment in the first hour — that's what makes the algorithm push you.")
    lines.append("📲 Full scripts live in our Claude chat.")
    lines.append("Go get it 🚀")
    return "\n".join(lines)


def build_week_message() -> str:
    schedule = json.loads(SCHEDULE.read_text())
    lines = [f"🗓 CJ CONTENT WEEK ({schedule.get('week_label', '')}) 🗓"]
    for date_key in sorted(schedule["dates"]):
        day = datetime.strptime(date_key, "%Y-%m-%d").strftime("%a %b %d").upper()
        lines.append(f"\n📅 {day}")
        lines += [f"{_emoji(_task_line(t))} {_task_line(t)}" for t in schedule["dates"][date_key]]
    lines.append("\n⏰ Your daily detail text arrives 7am every morning.")
    lines.append("📲 Scripts + captions live in our Claude chat.")
    lines.append("Big week. Let's build 🚀")
    return "\n".join(lines)


# Trial accounts prepend ~40 chars to every message; Twilio hard limit is 1600.
MAX_SMS_CHARS = 1400


def _chunks(body: str) -> list[str]:
    if len(body) <= MAX_SMS_CHARS:
        return [body]
    parts, current = [], ""
    for block in body.split("\n\n"):
        candidate = f"{current}\n\n{block}".strip()
        if len(candidate) > MAX_SMS_CHARS and current:
            parts.append(current)
            current = block
        else:
            current = candidate
    if current:
        parts.append(current)
    return [f"({i}/{len(parts)})\n{p}" for i, p in enumerate(parts, 1)]


def send_sms(body: str) -> None:
    sid = os.environ["TWILIO_ACCOUNT_SID"]
    token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ["TWILIO_FROM_NUMBER"]
    to_number = os.environ["MY_PHONE_NUMBER"]

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()

    for part in _chunks(body):
        data = urllib.parse.urlencode(
            {"From": from_number, "To": to_number, "Body": part}
        ).encode()
        request = urllib.request.Request(
            url, data=data, headers={"Authorization": f"Basic {auth}"}
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as resp:
                result = json.loads(resp.read())
            print(f"Sent part ({len(part)} chars): sid={result.get('sid')} status={result.get('status')}")
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")
            print(f"Twilio error {err.code}: {detail}")
            raise SystemExit(1)


def main() -> int:
    if "--today-file" in sys.argv:
        weekday, tasks = todays_tasks()
        message = build_message(weekday, tasks) if tasks else f"No content tasks today ({weekday})."
        out = Path(__file__).parent / "today.txt"
        out.write_text(message + "\n")
        print(f"Wrote {out} ({len(message)} chars)")
        return 0
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
