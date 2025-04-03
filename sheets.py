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

def send_to_sheets(username, date, processed_data, server=None):
    """
    Append a row to a Google Sheet with the processed data.

    Args:
        username (str): The username of the person who sent the message.
        date (str): The date and time when the message was sent.
        processed_data (dict): The structured data containing all extracted fields.
        server (str, optional): The server/guild from which the message originated. 
                               Used to determine which worksheet to update.

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

        # Default sheet name
        sheet_name = "Ticketkings Screenshots Data"
        worksheet_name = "Sheet1"  # Default worksheet
        
        # Determine which worksheet to use based on the server
        if server:
            server = server.lower()
            # Map server names to specific worksheets
            if "ticketkings hq" in server:
                worksheet_name = "Buying Data PH"
                logging.info(f"Using worksheet 'Buying Data PH' for server '{server}'")
            elif "ticket kings" in server:
                worksheet_name = "Buying Data US"
                logging.info(f"Using worksheet 'Buying Data US' for server '{server}'")
            elif "account testing" in server:
                sheet_name = "Account Testing Screenshots"
                worksheet_name = "Account Testing Data"
                logging.info(f"Using sheet '{sheet_name}' with worksheet '{worksheet_name}' for server '{server}'")
            else:
                logging.info(f"No specific mapping for server '{server}', using default worksheet")
        else:
            logging.info("No server specified, using default worksheet")
            
        logging.debug(f"Opening sheet: {sheet_name}")
        
        # Try to get the specific worksheet, defaulting to the first sheet if not found
        try:
            sheet = client.open(sheet_name).worksheet(worksheet_name)
            logging.info(f"Using worksheet: {worksheet_name}")
        except Exception as e:
            logging.warning(f"Could not access worksheet '{worksheet_name}': {e}")
            logging.info("Falling back to the default first sheet")
            sheet = client.open(sheet_name).sheet1
        
        # Parse the date to separate date and time
        # Handle different date formats
        try:
            # Try the standard format first
            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Try MM/DD/YY format
                date_obj = datetime.strptime(date, "%m/%d/%y")
                # Add current time if only date was provided
                now = datetime.now()
                date_obj = date_obj.replace(hour=now.hour, minute=now.minute, second=now.second)
            except ValueError:
                try:
                    # Try MM/DD/YYYY format
                    date_obj = datetime.strptime(date, "%m/%d/%Y")
                    now = datetime.now()
                    date_obj = date_obj.replace(hour=now.hour, minute=now.minute, second=now.second)
                except ValueError:
                    logging.warning(f"Could not parse date '{date}', using current date/time")
                    date_obj = datetime.now()

        formatted_date = date_obj.strftime("%m/%d/%Y")  # Format: MM/DD/YYYY
        # We're no longer sending the time separately based on the expected sheet format

        quantity_str = "".join(re.findall(
            r'\d+', str(processed_data.get("Quantity of Tickets", ""))))
        quantity = int(quantity_str) if quantity_str.isdigit() else 0

        # Updated row structure to match expected sheet columns
        row = [
            username,                                   # Purchaser Username
            formatted_date,                             # Date of Screenshot
            processed_data.get("Account Email", ""),    # Account Email
            processed_data.get("Account Password", ""), # Account Password
            processed_data.get("Event Name", ""),       # Event Name
            processed_data.get("Event Date", ""),       # Event Date
            processed_data.get("Venue", ""),            # Venue
            processed_data.get("Location", ""),         # Location
            quantity,                                   # Quantity of Tickets
            processed_data.get("Total Price", ""),      # Total Price
            processed_data.get("Last 4", ""),           # Last 4 of Card
            "",
            "",
            "",
            # username,                                   # Name (duplicate of username)
            # formatted_date,                             # Date (duplicate of date)
            # quantity,                                   # Qty Of Tickets (duplicate of quantity)
            processed_data.get("Website", "")           # Site
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
            
            # Format the duplicate date column (M)
            date_column2 = 'M'
            sheet.format(f'{date_column2}{added_row}', {
                'numberFormat': {
                    'type': 'DATE',
                    'pattern': 'M/d/yyyy'
                }
            })
            
            logging.info("Date formatting applied successfully.")
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
