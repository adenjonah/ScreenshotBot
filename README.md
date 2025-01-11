
# ScreenshotBot: Automating Screenshot Processing on Discord

## Overview

ScreenshotBot is a powerful Discord bot designed to streamline the extraction and organization of data from user-submitted screenshots and text in designated channels. Originally built as an automation solution for a ticket resale company, the bot helps to keep track of ticket order details submitted by employees, logging them into Google Sheets automatically. It integrates with OCR and AI technologies to extract structured information and logs it into Google Sheets for further analysis and reporting. This bot demonstrates skills in Python development, Discord bot design, OCR integration, and API usage, while ensuring robust error handling and security.

## Features

1. **Discord Integration**:
   - Listens for messages in specific channels (e.g., "screenshots").
   - Handles text content and image attachments seamlessly.
   - Provides real-time feedback to users via embeds in Discord.

2. **OCR and AI Integration**:
   - Uses OpenAI's GPT-4 and vision capabilities for text extraction from images.
   - Extracts structured data such as event details, ticket quantities, and pricing.

3. **Google Sheets Logging**:
   - Securely integrates with Google Sheets using OAuth2 credentials.
   - Automatically appends processed data to a Google Sheet for tracking.

4. **Error Handling and Cleanup**:
   - Logs errors and gracefully handles issues with data extraction or API calls.
   - Cleans up temporary files to maintain a secure and efficient environment.

## Technologies Used

- **Programming Language**: Python 3.10.12
- **Frameworks and Libraries**:
  - `discord.py` for Discord bot development.
  - `gspread` and `oauth2client` for Google Sheets API integration.
  - `openai` for GPT-4-based OCR and data extraction.
  - `pytesseract` as a backup OCR solution.
  - `dotenv` for secure environment variable management.
- **Environment**:
  - Hosted on a secure platform supporting Python runtime.

## Key Learning and Implementation Highlights

- **Building Bots with Discord.py**:
  Learned to handle events, commands, and manage permissions effectively.
  
- **OCR and AI-Driven Data Extraction**:
  Gained experience using GPT-4's multimodal capabilities to extract structured data from complex text and images.

- **API Integration**:
  Mastered working with the Google Sheets API and OAuth2 for secure data management.

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
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

This project represents a culmination of applied learning in AI, API integration, and Python development. It's a testament to my ability to design robust, scalable solutions while prioritizing performance and security.
