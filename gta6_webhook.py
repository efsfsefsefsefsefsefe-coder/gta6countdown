import time
from datetime import datetime, timezone
import requests

# Configuration
WEBHOOK_URL = "https://discord.com/api/webhooks/1568084057135251476/uWodNRGioKijzYxl9goyiDExfiWAdIuJIwMvZBv9KWkNkAguv-lVZPLI__zcl-RytHic"  # Replace with your actual Discord Webhook URL

# GTA 6 Release Date: November 19, 2026, 00:00 UTC
GTA6_RELEASE = datetime(2026, 11, 19, 0, 0, 0, tzinfo=timezone.utc)


def get_sleep_interval_and_time(remaining_seconds):
  """Determines the sleep duration in seconds based on time remaining."""
  if remaining_seconds > 7200:
    # More than 2 hours remaining: update every hour (3600s)
    return 3600
  elif remaining_seconds > 1800:
    # Between 30 mins and 2 hours remaining: update every 30 mins (1800s)
    return 1800
  else:
    # 30 minutes or less remaining: update every 1 minute (60s)
    return 60


def run_countdown():
  print("Starting GTA 6 webhook countdown loop...")
  message_id = None

  while True:
    now = datetime.now(timezone.utc)
    remaining = GTA6_RELEASE - now
    total_seconds = remaining.total_seconds()

    # Launch Trigger: Send release message with @everyone
    if total_seconds <= 0:
      payload = {
          "content": "@everyone",
          "embeds": [{
              "title": "🚨 GRAND THEFT AUTO VI IS OUT NOW! 🚨",
              "description": (
                  "The wait is officially over. Welcome back to Vice City,"
                  " Leonida!"
              ),
              "color": 0xFFD700,
          }],
      }
      if message_id:
        # Edit the final message to include the ping
        requests.patch(f"{WEBHOOK_URL}/messages/{message_id}", json=payload)
      else:
        requests.post(WEBHOOK_URL, json=payload)
      print("Launch message sent successfully!")
      break

    # Calculate days, hours, and minutes remaining
    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Determine dynamic update status
    sleep_interval = get_sleep_interval_and_time(total_seconds)
    if sleep_interval == 3600:
      frequency_label = "Auto-updates every hour"
    elif sleep_interval == 1800:
      frequency_label = "⚡ Auto-updates every 30 minutes"
    else:
      frequency_label = "🔥 Auto-updates every 1 minute!"

    # Build Embed Payload
    payload = {
        "embeds": [{
            "title": "🌴 Grand Theft Auto VI - Launch Countdown 🌴",
            "description": "Counting down to the release in Leonida.",
            "color": 0xFF0055,
            "fields": [{
                "name": "Time Remaining",
                "value": (
                    f"⏳ **{days}** days, **{hours}** hours, and"
                    f" **{minutes}** minutes"
                ),
                "inline": False,
            }],
            "footer": {
                "text": f"Target: November 19, 2026 | {frequency_label}"
            },
        }]
    }

    if message_id:
      # Edit the existing message via Webhook
      response = requests.patch(
          f"{WEBHOOK_URL}/messages/{message_id}", json=payload
      )
      if response.status_code != 200:
        # If the message was deleted or expired, post a new one
        post_response = requests.post(f"{WEBHOOK_URL}?wait=true", json=payload)
        if post_response.status_code == 200:
          message_id = post_response.json().get("id")
    else:
      # Post the initial message and store its ID for future edits
      post_response = requests.post(f"{WEBHOOK_URL}?wait=true", json=payload)
      if post_response.status_code == 200:
        message_id = post_response.json().get("id")

    # Wait for the calculated dynamic interval before the next update
    time.sleep(sleep_interval)


if __name__ == "__main__":
  run_countdown()