import gspread
from oauth2client.service_account import ServiceAccountCredentials

def send_to_sheets(processed_data):
    """
    Append a row to a Google Sheet with the processed data.

    Args:
        processed_data (dict): The structured data containing all extracted fields.

    Returns:
        str: Success or error message.
    """
    try:
        print("Initializing Google Sheets API...")
        
        # Define the scope for the Sheets API
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Path to your service account key file
        credentials_path = "screenshotbot-key.json"  # Replace with your downloaded JSON key file path
        print(f"Using credentials from: {credentials_path}")
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

        # Authorize the client
        client = gspread.authorize(credentials)
        print("Authorized Google Sheets client.")

        # Open the Google Sheet by name
        sheet_name = "ScreenshotBotTest"  # Replace with your sheet name
        print(f"Opening Google Sheet: {sheet_name}")
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

        print("Row to be appended:", row)

        # Append the row to the sheet
        sheet.append_row(row)
        print("Row successfully appended to the sheet.")

        return "Success"
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"Error: {e}"
