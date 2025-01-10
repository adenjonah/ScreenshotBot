import discord
from discord.ext import commands
import os
import aiohttp
from dotenv import load_dotenv
from gptOCR import gptOCR  # Import the OCR processing function
from process_data import process_order_data  # Import the data processing function
from sheets import send_to_sheets  # Import the function to send data to sheets

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive information
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
    print(f"Logged in as {bot.user.name} - {bot.user.id}")
    print("Bot is ready!")
    print("------")

@bot.command(name="logorder")
async def log_order(ctx):
    """
    Process an order message, extract text from attachments, and send data for further processing.
    """
    # Extract text content from the message
    order_text = ctx.message.content[len("!logorder "):].strip()  # Remove the command prefix
    if not order_text and not ctx.message.attachments:
        await ctx.send("Please provide order details or attach an image.")
        return

    # Initialize a list to store OCR results
    ocr_results = []
    downloaded_files = []  # Keep track of downloaded files

    # Handle image attachments
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                file_path = os.path.join(DOWNLOAD_DIR, attachment.filename)
                downloaded_files.append(file_path)  # Track file for cleanup

                # Download the image
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as response:
                        if response.status == 200:
                            with open(file_path, "wb") as f:
                                f.write(await response.read())
                            print(f"Image saved to {file_path}")

                            # Extract text from the image using gptOCR
                            ocr_data = gptOCR(file_path)
                            if "extracted_text" in ocr_data:
                                ocr_results.append(ocr_data["extracted_text"])
                            else:
                                await ctx.send(f"Failed to process {attachment.filename}. Error: {ocr_data.get('error', 'Unknown error')}")

                        else:
                            await ctx.send(f"Failed to download {attachment.filename}")

    # Combine text content and OCR results
    combined_data = {
        "text_content": order_text,
        "ocr_results": ocr_results
    }

    # Retrieve purchaser username and date of screenshot
    purchaser_username = ctx.author.name
    screenshot_date = ctx.message.created_at.strftime("%Y-%m-%d")

    print(f"combined data: {combined_data}")

    # Process the data using the process_data.py module
    processed_data = process_order_data(combined_data, purchaser_username, screenshot_date)

    print(f"processed data: {processed_data}")

    # Send the processed data to Google Sheets using sheets.py
    result = send_to_sheets(processed_data)

    # Notify the user of the result
    if result == "Success":
        await ctx.send("Order has been logged successfully!")
    else:
        await ctx.send("Failed to log the order. Please try again.")

    # Cleanup: Remove downloaded images
    for file_path in downloaded_files:
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Failed to delete file {file_path}: {e}")

# Run the bot
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN is None:
        print("Error: DISCORD_BOT_TOKEN not found in .env file.")
    else:
        bot.run(DISCORD_BOT_TOKEN)
