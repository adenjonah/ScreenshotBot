import json
import re
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_order_data(combined_data, purchaser_username, screenshot_date):
    """
    Process combined data to extract order information, send it to GPT API, and return structured JSON.

    Args:
        combined_data (dict): Contains 'text_content' and 'ocr_results' from user input and OCR processing.
        purchaser_username (str): The Discord username of the user who sent the message.
        screenshot_date (str): The date the screenshot message was sent (YYYY-MM-DD).

    Returns:
        dict: A structured JSON object with extracted fields.
    """
    try:
        # Extract text content and OCR results
        text_content = combined_data.get("text_content", "")
        ocr_results = combined_data.get("ocr_results", [])

        # Extract JSON from OCR results
        ocr_json = None
        for ocr_result in ocr_results:
            match = re.search(r"\{.*\}", ocr_result, re.DOTALL)
            if match:
                ocr_json = match.group()
                break

        # Debug: Log the extracted JSON
        print(f"OCR JSON extracted: {ocr_json}")

        # if not ocr_json:
        #     raise ValueError("No valid JSON found in OCR results.")

        # Prepare data for GPT API
        prompt = (
            f"Extract the following fields from the provided data and return them as a JSON object if you feel that the data you have been provided with is not intended to meet these classifications respond only with \"INPUT_ERROR_CODE\" and nothing else:\n\n"
            f"- Purchaser Username: The Discord username ({purchaser_username})\n"
            f"- Date of Screenshot: The date the screenshot was sent ({screenshot_date})\n"
            f"- Account Email: The email address in the text content\n"
            f"- Account Password: The password in the text content\n"
            f"- Event Name: The name of the event\n"
            f"- Event Date: The event date\n"
            f"- Venue: The venue name\n"
            f"- Location: City and State (Same field 'City, State')\n"
            f"- Quantity of Tickets: The number of tickets purchased\n"
            f"- Total Price: The total price in dollars\n\n"
            f"Data:\n\nText Content:\n{text_content}\n\nOCR Data:\n{ocr_json}\n\n"
            f"Ensure all fields are included in the JSON, even if null."
        )

        # Send request to OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a data extraction assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
        )

        # Extract the JSON from the response
        extracted_content = response.choices[0].message.content.strip()

        # Debug: Log the extracted content
        print(f"Extracted content: {extracted_content}")

        # Remove markdown code block delimiters if present
        if extracted_content.startswith("```") and extracted_content.endswith("```"):
            extracted_content = extracted_content[extracted_content.find("{"):extracted_content.rfind("}") + 1]

        if "INPUT_ERROR_CODE" in extracted_content:
            return {"error": "Input error code detected"}
        # Parse and return the extracted JSON
        return json.loads(extracted_content)

    except Exception as e:
        # Log the error
        print(f"Error during processing: {e}")
        return {"error": str(e)}
