import discord
from discord.ext import commands
import os
import aiohttp
import logging
from dotenv import load_dotenv
from gptOCR import gptOCR
from process_data import process_order_data
from sheets import send_to_sheets

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

command_prefix = "!"
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix=command_prefix, intents=intents)

DOWNLOAD_DIR = "downloaded_images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name} - {bot.user.id}")
    logging.info("Bot is ready!")


@bot.event
async def on_message(message):
    """
    Process any message in channels under the "screenshots" category.
    """

    if message.author == bot.user:
        return

    if message.channel.category is None or message.channel.category.name.lower() != "screenshots":
        return

    order_text = message.content.strip()
    if not order_text and not message.attachments:
        logging.info("Message ignored: No text or attachments found.")
        return

    ocr_results = []
    downloaded_files = []

    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                file_path = os.path.join(DOWNLOAD_DIR, attachment.filename)
                downloaded_files.append(file_path)

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as response:
                            if response.status == 200:
                                with open(file_path, "wb") as f:
                                    f.write(await response.read())
                                logging.info(f"Image saved to {file_path}")

                                ocr_data = gptOCR(file_path)
                                if "extracted_text" in ocr_data:
                                    ocr_results.append(
                                        ocr_data["extracted_text"])
                                else:
                                    logging.warning(
                                        f"Failed to process {attachment.filename}: {ocr_data.get('error', 'Unknown error')}")
                            else:
                                logging.error(
                                    f"Failed to download {attachment.filename}")
                except Exception as e:
                    logging.error(
                        f"Error downloading or processing image: {attachment.filename}. Error: {e}")

    combined_data = {
        "text_content": order_text,
        "ocr_results": ocr_results
    }

    purchaser_username = message.author.name
    screenshot_date = message.created_at.strftime("%Y-%m-%d")

    logging.info(f"Combined data: {combined_data}")

    try:

        processed_data = process_order_data(
            combined_data, purchaser_username, screenshot_date)
        logging.info(f"Processed data: {processed_data}")

        if processed_data.get("error"):
            logging.warning(
                f"Processing error detected: {processed_data['error']}")
            return

        MAX_ALLOWED_MISSING_FIELDS = 3

        required_fields = ["Account Email", "Event Name", "Event Date",
                           "Location", "Quantity of Tickets", "Total Price"]
        missing_fields = [
            field for field in required_fields if not processed_data.get(field)]

        if len(missing_fields) > MAX_ALLOWED_MISSING_FIELDS:
            logging.warning(
                f"Too many missing required fields: {missing_fields}. Skipping logging.")
            return
        else:
            logging.info(
                f"Proceeding despite missing fields: {missing_fields}")

        result = send_to_sheets(processed_data)
        if result == "Success":
            embed = discord.Embed(
                title="Order Logged Successfully!",
                description="Here is the information that was logged. Please review it for accuracy.",
                color=discord.Color.green()
            )
            for key, value in processed_data.items():

                if value is None or str(value).lower() == "none":
                    embed.add_field(name=key, value=f"🔴 None", inline=True)
                else:
                    embed.add_field(name=key, value=value, inline=True)

            await message.channel.send(embed=embed)
        else:
            logging.error(f"Failed to log order: {result}")
    except Exception as e:
        logging.error(
            f"Error during processing or logging to Google Sheets: {e}")

    for file_path in downloaded_files:
        try:
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")
        except Exception as e:
            logging.error(f"Failed to delete file {file_path}: {e}")

if __name__ == "__main__":
    if DISCORD_BOT_TOKEN is None:
        logging.critical("Error: DISCORD_BOT_TOKEN not found in .env file.")
    else:
        bot.run(DISCORD_BOT_TOKEN)
