
# ScreenshotBot: Automating Screenshot Processing on Discord

## Overview

ScreenshotBot is a powerful Discord bot designed to streamline the extraction and organization of data from user-submitted screenshots and text in designated channels. Originally built as an automation solution for a ticket resale company, the bot helps to keep track of ticket order details submitted by employees, logging them into Google Sheets automatically. Additionally, the bot now integrates with ClickUp to create tasks for each processed entry, ensuring streamlined task management. It demonstrates skills in Python development, Discord bot design, OCR integration, API usage, asynchronous processing, and robust error handling.

## Features

1. **Discord Integration**:
   - Listens for messages in specific channels (e.g., "screenshots").
   - Handles text content and image attachments seamlessly.
   - Provides real-time feedback to users via embeds in Discord.

2. **Asynchronous Message Processing**:
   - Uses asyncio to process multiple messages concurrently for high performance.
   - Ensures quick responses to users while handling background tasks efficiently.

3. **OCR and AI Integration**:
   - Uses OpenAI's GPT-4 and vision capabilities for text extraction from images.
   - Extracts structured data such as event details, ticket quantities, and pricing.

4. **Google Sheets Logging**:
   - Securely integrates with Google Sheets using OAuth2 credentials.
   - Automatically appends processed data to a Google Sheet for tracking.

5. **ClickUp Task Integration**:
   - Creates tasks in a ClickUp list for each processed message.
   - Includes custom fields for details such as the screenshot date, ticket quantity, and associated team member.
   - Ensures accurate task assignment based on a username-to-team mapping.

6. **Error Handling and Cleanup**:
   - Logs errors and gracefully handles issues with data extraction or API calls.
   - Cleans up temporary files to maintain a secure and efficient environment.

7. **Hosted on Heroku**:
   - The bot is deployed on Heroku, ensuring reliability, scalability, and 24/7 uptime.

## Technologies Used

- **Programming Language**: Python 3.10.12
- **Frameworks and Libraries**:
  - `discord.py` for Discord bot development.
  - `gspread` and `oauth2client` for Google Sheets API integration.
  - `openai` for GPT-4-based OCR and data extraction.
  - `pytesseract` as a backup OCR solution.
  - `requests` for ClickUp API integration.
  - `pytz` for timezone management.
  - `dotenv` for secure environment variable management.
- **Environment**:
  - Hosted on Heroku supporting Python runtime.

## Key Learning and Implementation Highlights

- **Building Bots with Discord.py**:
  Learned to handle events, commands, and manage permissions effectively.
  
- **OCR and AI-Driven Data Extraction**:
  Gained experience using GPT-4's multimodal capabilities to extract structured data from complex text and images.

- **Asynchronous Processing**:
  Implemented message queues and asyncio to process multiple Discord messages concurrently for improved performance.

- **API Integration**:
  Mastered working with the Google Sheets API, OAuth2, and ClickUp API for secure data and task management.

- **Secure Development Practices**:
  Employed `dotenv` to manage API keys and other sensitive information securely.

- **Error Logging and Recovery**:
  Implemented robust logging using Python's `logging` module for debugging and issue resolution.

- **Automated Data Pipeline**:
  Designed an end-to-end system for processing, validating, and logging data in real time.

## Getting Started

### Prerequisites

- Python 3.10+ installed.
- Discord bot token.
- OpenAI API key.
- Google Sheets credentials in JSON format.
- ClickUp API token.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/adenjonah/screenshotbot.git
   cd screenshotbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in a `.env` file:
   ```env
   DISCORD_BOT_TOKEN=your_discord_token
   OPENAI_API_KEY=your_openai_key
   GOOGLE_KEY='{"type": "service_account", ...}'
   CLICKUP_API_TOKEN=your_clickup_api_token
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Additional Notes

- **ClickUp Integration**:
  - Tasks created in ClickUp include:
    - `Date of Screenshot` (localized to Eastern Time).
    - `Quantity of Tickets`.
    - `Buying Team` (mapped from usernames to team names).
  - Ensure the ClickUp list ID is configured correctly in the bot.

- **Timezone Handling**:
  - Dates are converted to Eastern Time (ET) before logging or task creation.

This project represents a culmination of applied learning in AI, API integration, and Python development. It's a testament to my ability to design robust, scalable solutions while prioritizing performance and security.
