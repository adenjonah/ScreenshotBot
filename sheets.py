import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import logging
import re
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,  # Changed from DEBUG to INFO
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def send_to_sheets(username, date, processed_data):
    """
    Append a row to a Google Sheet with the processed data.

    Args:
        processed_data (dict): The structured data containing all extracted fields.

    Returns:
        str: Success or error message.
    """
    logging.debug("Initializing Google Sheets connection...")

    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]

        google_key_json = os.getenv("GOOGLE_KEY")
        if not google_key_json:
            logging.error("GOOGLE_KEY environment variable is not set.")
            raise ValueError("GOOGLE_KEY environment variable is not set.")

        logging.debug("Decoding service account credentials...")
        service_account_info = json.loads(google_key_json)
        logging.info("Service account info successfully loaded.")

        # data_file_path = "greg-key.json"

        # if not os.path.exists(data_file_path):
        #     logging.error(
        #         f"{data_file_path} not found. Ensure the file is in the project directory.")
        #     raise FileNotFoundError(f"{data_file_path} not found.")

        # logging.debug(
        #     f"Loading service account credentials from {data_file_path}...")
        # with open(data_file_path, "r") as file:
        #     service_account_info = json.load(file)
        # logging.info("Service account info successfully loaded.")

        logging.debug("Creating credentials from the service account info...")
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            service_account_info, scope)
        logging.info("Credentials successfully created.")

        logging.debug("Authorizing the Google Sheets client...")
        client = gspread.authorize(credentials)
        logging.info("Google Sheets client authorized successfully.")

        sheet_name = "Ticketkings Screenshots Data"
        logging.debug(f"Opening sheet: {sheet_name}")
        sheet = client.open(sheet_name).sheet1
        
        # Parse the date to separate date and time
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S") 
        formatted_date = date_obj.strftime("%m/%d/%Y")  # Format: MM/DD/YYYY
        formatted_time = date_obj.strftime("%I:%M:%S %p")  # Format: HH:MM:SS AM/PM

        quantity_str = "".join(re.findall(
            r'\d+', str(processed_data.get("Quantity of Tickets", ""))))
        quantity = int(quantity_str) if quantity_str.isdigit() else 0

        row = [
            username,
            formatted_date,
            formatted_time,
            processed_data.get("Event Name", ""),
            processed_data.get("Venue", ""),
            processed_data.get("Location", ""),
            processed_data.get("Website", ""),
            quantity,
            processed_data.get("Total Price", ""),
            processed_data.get("Last 4", "")
        ]

        logging.debug(f"Prepared row to append: {row}")

        logging.debug("Appending row to the Google Sheet...")
        response = sheet.append_row(row, value_input_option='USER_ENTERED')
        
        try:
            # Get the added row index
            all_values = sheet.get_all_values()
            added_row = len(all_values)
            logging.info(f"Row successfully appended at row {added_row}.")
            
            # Format the date column (second column - B)
            date_column = 'B'
            sheet.format(f'{date_column}{added_row}', {
                'numberFormat': {
                    'type': 'DATE',
                    'pattern': 'M/d/yyyy'
                }
            })
            
            # Format the time column (third column - C)
            time_column = 'C'
            sheet.format(f'{time_column}{added_row}', {
                'numberFormat': {
                    'type': 'TIME',
                    'pattern': 'h:mm:ss AM/PM'
                }
            })
            
            logging.info("Date and time formatting applied successfully.")
        except Exception as format_error:
            logging.error(f"Error formatting date/time cells: {format_error}")
            # Continue even if formatting fails
        
        logging.info(f"Successfully logged order for {username}")
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
