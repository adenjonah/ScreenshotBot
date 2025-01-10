import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    """
    Encodes an image in base64 format for sending to OpenAI Vision API.
    Args:
        image_path (str): Path to the image file.
    Returns:
        str: Base64-encoded string of the image.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to encode image: {e}")

def gptOCR(image_path):
    """
    Uses OpenAI Vision to extract text or understand content from an image.
    Args:
        image_path (str): Path to the image file.
    Returns:
        dict: Extracted content or error details.
    """
    try:
        # Encode the image in base64
        base64_image = encode_image(image_path)

        # Create the API request
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the vision-capable model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "Extract the following information from the image and return it as a JSON object with no leading or trailing text: "
                            "Event Name, Event Date (MM/DD/YYYY format), Venue, Location (City, State), Quantity of tickets purchased, "
                            "and Total price in $. Do not include any other text in your response."
                        )},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",  # Use high-detail mode
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        # Return the extracted text
        return {"file_path": image_path, "extracted_text": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"file_path": image_path, "error": str(e)}

# Example Usage
if __name__ == "__main__":
    # Path to the image
    image_path = "test1.png"

    # Run the OCR
    raw_result = gptOCR(image_path)
    result = re.search(r"\{.*\}", raw_result["extracted_text"], re.DOTALL).group()

    # Print the results
    if "extracted_text" in raw_result:
        print(result)
    else:
        print("Error:")
        print(raw_result["error"])
