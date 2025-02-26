import json
import re
import os
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv


load_dotenv()


openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def process_order_data(combined_data, purchaser_username, screenshot_date):
    """
    Process combined data to extract order information, send it to GPT API, and return structured JSON.

    Args:
        combined_data (dict): Contains 'text_content' and 'ocr_results' from user input and OCR processing.
        purchaser_username (str): The Discord username of the user who sent the message.
        screenshot_date (str): The date the screenshot message was sent (YYYY-MM-DD).

    Returns:
        dict: A structured JSON object with extracted fields or an error message if invalid input.
    """
    try:

        text_content = combined_data.get("text_content", "").strip()
        ocr_results = combined_data.get("ocr_results", [])

        print(f"Received text content: {text_content}")
        print(f"Received OCR results: {ocr_results}")

        if not text_content and not ocr_results:
            return {"error": "No valid content found in the input."}

        ocr_json = None
        for ocr_result in ocr_results:
            match = re.search(r"\{.*\}", ocr_result, re.DOTALL)
            if match:
                ocr_json = match.group()
                break

        print(f"OCR JSON extracted: {ocr_json}")

        prompt = (
            f"Extract the following fields from the provided data and return them as a JSON object. "
            f"If you feel the data is not intended for these classifications, respond only with \"INPUT_ERROR_CODE\":\n\n"
            f"- Account Email: The email address of the purchaser\n"
            f"- Account Password: The password, if unsure what the password is use any chunk with words numbers and symbols\n"
            f"- Event Name: The name of the event\n"
            f"- Event Date: The event date\n"
            f"- Venue: The venue name\n"
            f"- Location: City and State (Same field 'City, State' with two letter state code)\n"
            f"- Quantity of Tickets: The number of tickets purchased. If the quantity is provided in the text content (ex. quantity 8, qty 8, 8x, quantity 4, qty 4, 4x, and others) use the provided text over what you get in the OCR. Also, only return the numeric value (8 for 8x, 8 tickets, qty 8 etc)\n"
            f"- Total Price: The total price in dollars\n"
            f"- Last 4: The last 4 digits of the credit card that made the purchase\n\n"
            f"Data:\n\nText Content:\n{text_content}\n\nOCR Data:\n{ocr_json}\n\n"
            f"Ensure all fields are included in the JSON, even if null."
        )

        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        extracted_content = response.choices[0].message.content.strip()

        print(f"Extracted content: {extracted_content}")

        if "INPUT_ERROR_CODE" in extracted_content:
            return {"error": "Input does not match the expected order format."}

        if extracted_content.startswith("```") and extracted_content.endswith("```"):
            extracted_content = extracted_content[extracted_content.find(
                "{"):extracted_content.rfind("}") + 1]

        return json.loads(extracted_content)

    except Exception as e:

        print(f"Error during processing: {e}")
        return {"error_code": "PROCESSING_ERROR"}
