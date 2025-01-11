import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG level for detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Logs to console
    ]
)

def send_to_sheets(processed_data):
    """
    Append a row to a Google Sheet with the processed data.

    Args:
        processed_data (dict): The structured data containing all extracted fields.

    Returns:
        str: Success or error message.
    """
    logging.info("Initializing Google Sheets API...")

    try:
        # Define the scope for the Sheets API
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # Load service account credentials from the GOOGLE_KEY environment variable
        google_key_json = os.getenv("GOOGLE_KEY")
        if not google_key_json:
            logging.error("GOOGLE_KEY environment variable is not set.")
            raise ValueError("GOOGLE_KEY environment variable is not set.")

        logging.debug("Decoding service account credentials...")
        service_account_info = json.loads(google_key_json)
        logging.info("Service account info successfully loaded.")

        logging.debug("Creating credentials from the service account info...")
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        logging.info("Credentials successfully created.")

        # Authorize the client
        logging.debug("Authorizing the Google Sheets client...")
        client = gspread.authorize(credentials)
        logging.info("Google Sheets client authorized successfully.")

        # Open the Google Sheet by name
        sheet_name = "BuyingScreenshotsData"  # Replace with your sheet name
        logging.info(f"Opening Google Sheet: {sheet_name}")
        sheet = client.open(sheet_name).sheet1

        # Extract data from processed_data
        row = [
            processed_data.get("Purchaser Username", ""),
            processed_data.get("Date of Screenshot", ""),
            processed_data.get("Account Email", ""),
            processed_data.get("Account Password", ""),
            processed_data.get("Event Name", ""),
            processed_data.get("Event Date", ""),
            processed_data.get("Venue", ""),
            processed_data.get("Location", ""),
            processed_data.get("Quantity of Tickets", ""),
            processed_data.get("Total Price", "")
        ]

        logging.debug(f"Prepared row to append: {row}")

        # Append the row to the sheet
        logging.debug("Appending row to the Google Sheet...")
        sheet.append_row(row)
        logging.info("Row successfully appended to the Google Sheet.")

        return "Success"

    except gspread.exceptions.SpreadsheetNotFound as snf_error:
        logging.error(f"Spreadsheet '{sheet_name}' not found: {snf_error}")
        return f"Error: Spreadsheet '{sheet_name}' not found."

    except gspread.exceptions.APIError as api_error:
        logging.error(f"Google API error: {api_error}")
        return f"Error: Google API error: {api_error}"

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return f"Error: {e}"