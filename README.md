Live example:
youtube.com/watch?v=GA1Rqz2RzCg

Crypto Trading Bot - Telegram Integration
Overview
This project is a Telegram bot that provides cryptocurrency trading analysis and database management functionalities. It integrates with Binance for market data and offers AI-powered analysis of various cryptocurrencies.

Features
User Authentication:

Secure login with private keys

User registration with email and API key storage

Login attempt limiting for security

Cryptocurrency Analysis:

Short-term and long-term market predictions

Custom analysis with user-defined parameters

Multiple time interval options (1m, 5m, 15m, 1h, 6h, 1d)

Database Management:

Add/remove cryptocurrencies from tracking list

View current tracked cryptocurrencies

User Interface:

Interactive inline keyboards

Menu-driven navigation

Attractive button formatting with emojis

Technical Components
Backend:

SQLite database for user and cryptocurrency data

Binance API integration for market data

AI analysis module (aianalyz.py)

Security:

Private key generation for user authentication

API key storage in encrypted database

Login attempt tracking and limiting

Installation
Clone the repository:

Copy
git clone [repository-url]
cd [repository-directory]
Install required dependencies:

Copy
pip install -r requirements.txt
Set up environment:

Create a .env file with your Telegram bot token:

Copy
TELEGRAM_BOT_TOKEN=your_bot_token_here
Initialize the database:

Run the script once to create the necessary tables.

Usage
Start the bot:

Copy
python main.py
Interact with the bot through Telegram:

Send /start to begin

Follow the menu options to:

Login/register

Analyze cryptocurrencies

Manage your tracked coins

Logout

Commands
/start - Begin interaction with the bot

/Crypto Analyse - Analyze selected cryptocurrencies

/EditDB - Manage your tracked cryptocurrencies

/Logout - End your session

Database Schema
The bot uses two main tables:

users:

user_id (INTEGER PRIMARY KEY)

private_key (TEXT)

email (TEXT)

api_key (TEXT)

groups:

tags (TEXT) - Stores cryptocurrency symbols

Error Handling
The bot includes:

Automatic reconnection on errors

Input validation

Clear error messages for users

Attempt limiting for security

Dependencies
python-telegram-bot

sqlite3

binanceTrader (custom module)

aianalyz (custom module)

secrets (for secure key generation)

datetime, time (for time operations)

re (for input validation)

Customization
To customize the bot:

Modify the analysis parameters in aianalyz.py

Adjust the time intervals in the analysis functions

Update the database schema as needed
