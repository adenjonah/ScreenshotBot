import os
import requests
import time
from dotenv import load_dotenv
import logging
import pytz
from datetime import datetime

load_dotenv()

CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN")
CLICKUP_API_BASE = "https://api.clickup.com/api/v2"

# Configure logging for the ClickUp module
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(message)s")

# Define the username-to-tag mapping dictionary
USERNAME_TO_TAG = {
    "tiyu321": "Tiyu",
    "sammylby": "Sammuguru",
    "sausagenft": "Sausage",
    "oomanueloo": "Manuel",
    "era8605": "Era",
    "harvey03": "Raive",
    "clnoo": "Christine",
    "rhea07537": "Rhea",
    "jeleen0405": "Jeleen",
    "mariaeden_": "Eden",
    "mistysun_": "Mistysun",
    "xavieryyyyy2740": "Xaviery",
    "stephaniemaem": "Hopey",
    "adenj_": "Hopey"
}

# Define the team tag-to-ID mapping dictionary
BUYING_TEAM_OPTIONS = {
    "Manuel": "f7660ece-9213-41c2-bede-5c3ecfb989b4",
    "Sammuguru": "c60db83f-a227-4785-abb6-7eb910eb6e36",
    "Rhea": "2de28b53-4d53-4f0b-bb4f-4bf6a7b997a8",
    "Raive": "02f8269a-3a64-4108-919f-f2fec113f969",
    "Christine": "35fec3ef-7855-484d-81d5-c30bfcb723ce",
    "Era": "f5bc43e4-438e-4471-ae66-5d6873a6e4c2",
    "Hopey": "fc72b40c-4244-4caf-a670-86ad1986c8bb",
    "Sausage": "d7c31824-0869-4888-b656-5e45dc8fddf3",
    "Tiyu": "329713f4-d3f1-44a0-a32b-04ec697d9ba4",
    "Mistysun": "dd37b33a-0117-42ce-a5a8-c4b3026f858a",
    "Xaviery": "f481d7bb-e21e-40e6-b812-5ae48df41062",
    "Jeleen": "bbca2379-ca4f-42b8-b413-fbfcb38a776c",
    "Eden": "a1f26441-8d44-461b-aa0f-73463319146b",
    "Arphie": "678639ea-ec39-491d-aa6a-0d5de1f74f17",
    "Christian": "4bb844d6-3808-4307-b9ca-e5082239bfac",
    "Chester": "f628b438-d3a9-4e73-9075-ca7fde0b6cf7"
}


def append_to_clickup_task(list_id, username, date_of_screenshot, quantity_of_tickets):
    """
    Create a task in the specified ClickUp list with custom fields.
    """
    if username not in USERNAME_TO_TAG:
        logging.error(
            f"Username '{username}' not found in mapping. Skipping task creation.")
        return f"Error: Username '{username}' not found in mapping."

    team_tag = USERNAME_TO_TAG[username]
    team_uuid = BUYING_TEAM_OPTIONS.get(team_tag)

    if not team_uuid:
        logging.error(
            f"Invalid team tag '{team_tag}' for username '{username}'.")
        return f"Error: Invalid team tag '{team_tag}' for username '{username}'."

    logging.debug(f"Resolved team tag '{team_tag}' to UUID: {team_uuid}")

    # Handle date parsing and conversion to Eastern Time
    try:
        # Parse date in MM/DD/YY format
        try:
            naive_date = datetime.strptime(date_of_screenshot, "%m/%d/%y")
        except ValueError:
            # Fallback to YYYY-MM-DD format
            naive_date = datetime.strptime(date_of_screenshot, "%Y-%m-%d")

        # Localize to Eastern Time (ET)
        eastern = pytz.timezone("US/Eastern")
        localized_date = eastern.localize(naive_date)

        # Convert to milliseconds since epoch
        date_in_ms = int(localized_date.timestamp() * 1000)
    except ValueError as e:
        logging.error(
            f"Invalid date format: {date_of_screenshot}. Expected format is MM/DD/YY or YYYY-MM-DD. Error: {e}")
        return f"Error: Invalid date format '{date_of_screenshot}'. Expected MM/DD/YY or YYYY-MM-DD."

    url = f"{CLICKUP_API_BASE}/list/{list_id}/task"
    headers = {
        "Authorization": CLICKUP_API_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "name": username,
        "custom_fields": [
            {
                "id": "93467127-e21f-45e5-b90e-052c2f9cf332",  # Date of Screenshot
                "value": date_in_ms
            },
            {
                "id": "abc0669f-685b-45ab-a7d7-c2f2f7573119",  # Quantity of Tickets
                "value": quantity_of_tickets
            },
            {
                "id": "c67a5727-32c8-4638-80a0-f3b1f4de7a70",  # Buying Team
                "value": team_uuid
            }
        ]
    }

    logging.debug(f"Sending payload to ClickUp: {payload}")

    response = requests.post(url, headers=headers, json=payload)
    logging.info(f"ClickUp response: {response.status_code} - {response.text}")

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(f"Failed to create ClickUp task: {e}")
        logging.error(f"Response content: {response.json()}")
        return f"Error: {response.json().get('err', 'Unknown error')} (Code: {response.status_code})"

    return response.json()
