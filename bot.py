import discord
from discord.ext import commands
import os
import aiohttp
import logging
from dotenv import load_dotenv
from gptOCR import gptOCR  # Import the OCR processing function
from process_data import process_order_data  # Import the data processing function
from sheets import send_to_sheets  # Import the function to send data to sheets

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Set log level to INFO or DEBUG for more detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Logs to Heroku stdout
    ]
)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Define command prefix
command_prefix = "!"
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Required to read message content

# Initialize the bot
bot = commands.Bot(command_prefix=command_prefix, intents=intents)

# Directory to save downloaded images
DOWNLOAD_DIR = "downloaded_images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure the directory exists

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name} - {bot.user.id}")
    logging.info("Bot is ready!")

@bot.event
async def on_message(message):
    """
    Process any message in channels under the "screenshots" category.
    """
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Check if the channel belongs to the "screenshots" category
    if message.channel.category is None or message.channel.category.name.lower() != "screenshots":
        return

    # Extract text content from the message
    order_text = message.content.strip()  # Remove leading and trailing whitespace
    if not order_text and not message.attachments:
        await message.channel.send("Please provide order details or attach an image.")
        return

    ocr_results = []
    downloaded_files = []  # Keep track of downloaded files

    # Handle image attachments
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                file_path = os.path.join(DOWNLOAD_DIR, attachment.filename)
                downloaded_files.append(file_path)  # Track file for cleanup

                try:
                    # Download the image
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as response:
                            if response.status == 200:
                                with open(file_path, "wb") as f:
                                    f.write(await response.read())
                                logging.info(f"Image saved to {file_path}")

                                # Extract text from the image using gptOCR
                                ocr_data = gptOCR(file_path)
                                if "extracted_text" in ocr_data:
                                    ocr_results.append(ocr_data["extracted_text"])
                                else:
                                    await message.channel.send(f"Failed to process {attachment.filename}. Error: {ocr_data.get('error', 'Unknown error')}")
                            else:
                                await message.channel.send(f"Failed to download {attachment.filename}")
                except Exception as e:
                    logging.error(f"Error downloading or processing image: {attachment.filename}. Error: {e}")

    combined_data = {
        "text_content": order_text,
        "ocr_results": ocr_results
    }

    purchaser_username = message.author.name
    screenshot_date = message.created_at.strftime("%Y-%m-%d")

    logging.info(f"Combined data: {combined_data}")

    try:
        # Process the data
        processed_data = process_order_data(combined_data, purchaser_username, screenshot_date)
        logging.info(f"Processed data: {processed_data}")

        if processed_data.get("error"):
            await message.channel.send("Failed to process the order. Please try again.")
            return
        # Send to Google Sheets
        result = send_to_sheets(processed_data)
        if result == "Success":
            embed = discord.Embed(
                title="Order Logged Successfully!",
                description="Here is the information that was logged. Please review it for accuracy.",
                color=discord.Color.green()
            )
            for key, value in processed_data.items():
                # If the value is None or "None", prepend a red circle emoji
                if value is None or str(value).lower() == "none":
                    embed.add_field(name=key, value=f"🔴 None", inline=True)  # Use red circle emoji for emphasis
                else:
                    embed.add_field(name=key, value=value, inline=True)

            await message.channel.send(embed=embed)
        else:
            await message.channel.send("Failed to log the order. Please try again.")
            logging.error(f"Failed to log order: {result}")
    except Exception as e:
        logging.error(f"Error during processing or logging to Google Sheets: {e}")

    # Cleanup
    for file_path in downloaded_files:
        try:
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")
        except Exception as e:
            logging.error(f"Failed to delete file {file_path}: {e}")

# Run the bot
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN is None:
        logging.critical("Error: DISCORD_BOT_TOKEN not found in .env file.")
    else:
        bot.run(DISCORD_BOT_TOKEN)
