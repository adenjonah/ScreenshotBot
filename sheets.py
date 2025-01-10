import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def get_credentials():
    """
    Reconstructs Google service account credentials from environment variables.
    """
    # Reconstruct JSON key from environment variables
    service_account_info = {
        "type": "service_account",
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),  # Replace escaped newlines
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL"),
    }

    # Create credentials using the reconstructed JSON
    return ServiceAccountCredentials.from_json_keyfile_dict(service_account_info)

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

        # Get credentials from environment variables
        credentials = get_credentials()
        print("Credentials successfully reconstructed from environment variables.")

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
            f'{processed_data.get("Location", {}).get("City", "")}, {processed_data.get("Location", {}).get("State", "")}',
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
