import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

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
        base64_image = encode_image(image_path)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "Extract the following information from the image and return it as a JSON object with no leading or trailing text: "
                            "Event Name, Event Date (MM/DD/YYYY format), Venue, Location (City, State (Two letter state code)), Quantity of tickets purchased, "
                            "and Total price in $. Last 4 of the credit card used for purchase. The quantity and total price should include all tickets in the order, even if they are different types"
                            "Like if 2 are VIP and 3 are general, total quantity is 5. Do not include any other text in your response."
                        )},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )

        return {"file_path": image_path, "extracted_text": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"file_path": image_path, "error": str(e)}


if __name__ == "__main__":
    image_path = "test1.png"

    raw_result = gptOCR(image_path)
    result = re.search(
        r"\{.*\}", raw_result["extracted_text"], re.DOTALL).group()

    if "extracted_text" in raw_result:
        print(result)
    else:
        print("Error:")
        print(raw_result["error"])
