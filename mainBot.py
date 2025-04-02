import time
from datetime import datetime, timedelta
import telebot
from telebot import types
import re
import sqlite3
import secrets
from binanceTrader import coinTrader
import aianalyz

bot = telebot.TeleBot("")
# In-memory storage to keep track of logged-in users
logged_in_users = set()
login_attempts = {}  # Dictionary to store login attempts
bnbot = coinTrader()
users_state = {}  # Tracks the current state of a user
users_data = {}  # Optionally, store any data needed to process the input

# Function to create a new SQLite connection and cursor
def create_db_connection():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    return conn, cursor


# Function to generate a random private key
def generate_private_key():
    return secrets.token_hex(16)  # 16 bytes gives a 32-character hex string


# Function to create the 'users' table if it doesn't exist
def create_users_table():
    conn, cursor = create_db_connection()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            private_key TEXT,
            email TEXT,
            api_key TEXT
        )
    ''')
    conn.commit()
    conn.close()

def check_private_key(message):
    user_id = message.from_user.id
    private_key = message.text

    # Check if the user has attempted to login multiple times
    login_attempts_key = f"login_attempts:{user_id}"
    current_attempts = login_attempts.get(login_attempts_key, 0)

    # Set the maximum allowed attempts
    max_attempts = 3

    if current_attempts >= max_attempts:
        # User exceeded the maximum allowed attempts
        bot.send_message(message.chat.id, "Maximum login attempts exceeded. Please try again later.")
    else:
        # Check if the private key is in the database
        conn, cursor = create_db_connection()
        cursor.execute("SELECT * FROM users WHERE private_key=?", (private_key,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            # Valid private key, reset the attempts and show options
            login_user(user_id)
            show_options(message.chat.id)
            login_attempts[login_attempts_key] = 0
        else:
            # Invalid private key, increment the attempts
            login_attempts[login_attempts_key] = current_attempts + 1
            bot.send_message(message.chat.id,
                             f"Login failed. You have {max_attempts - current_attempts - 1} attempts left. Please try again.")
            bot.register_next_step_handler(message, check_private_key)


# Function to register the user
def register_user(message):
    try:
        user_id = message.from_user.id
        email = message.text

        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            # Prompt the user for their API key
            bot.send_message(message.chat.id, "Please enter your API key:")
            bot.register_next_step_handler(message, finish_registration, email)

    except:
        bot.send_message(message.chat.id, "An error occurred. Please try again.")


def finish_registration(message, email):
    user_id = message.from_user.id
    api_key = message.text
    private_key = generate_private_key()

    conn, cursor = create_db_connection()
    cursor.execute("INSERT INTO users (user_id, email, private_key, api_key) VALUES (?, ?, ?, ?)",
                   (user_id, email, private_key, api_key))
    conn.commit()
    conn.close()

    login_user(user_id)
    show_options(message.chat.id)
    bot.send_message(message.chat.id, f"Registration successful!\nYour private key is: {private_key}")


# Create the 'users' table if
def get_user_aiapi(user_id):
    conn, cursor = create_db_connection()
    cursor.execute("SELECT api_key FROM users WHERE user_id=?", (user_id,))
    aiapi = cursor.fetchone()
    conn.close()
    return aiapi[0] if aiapi else None


def addtoDB(name):
    conn, cursor = create_db_connection()
    cursor.execute('INSERT INTO groups (tags) VALUES (?)', (name,))
    conn.commit()
    conn.close()


def returnGroups():
    conn, cur = create_db_connection()
    cur.execute("SELECT * FROM groups")
    rows = cur.fetchall()  # Fetch all rows from the result set
    groups = [row[0] for row in rows]  # Extract the first element from each row and store in a list
    return groups


def delgroup(group):
    conn, cur = create_db_connection()
    cur.execute("DELETE FROM groups WHERE tags = ?", (group,))
    conn.commit()
    conn.close()


# Function to log in the user and update the logged_in_users set
def login_user(user_id):
    logged_in_users.add(user_id)


# Function to log out the user and update the logged_in_users set
def logout_user(user_id):
    logged_in_users.discard(user_id)


# Command handler for the /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id

    if user_id in logged_in_users:
        # User is already logged in, show options
        show_options(message.chat.id)
    else:
        # User is not logged in, show login/register options
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Login")
        item2 = types.KeyboardButton("Register")
        markup.add(item1, item2)

        bot.send_message(message.chat.id, "Welcome! Choose an option:", reply_markup=markup)


# Handler for the "Login" button
@bot.message_handler(func=lambda message: message.text == "Login")
def handle_login(message):
    user_id = message.from_user.id

    if user_id in logged_in_users:
        # User is already logged in, show options
        show_options(message.chat.id)
    else:
        # User is not logged in, proceed with login
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Please enter your private key:", reply_markup=markup)
        bot.register_next_step_handler(message, check_private_key)


@bot.message_handler(commands=['EditDB'])
def handle_editDB(message):
    grupn = returnGroups()
    response = "Here are the current groups:\n"
    response += "\n".join([f"{idx + 1}. {name}" for idx, name in enumerate(grupn)])
    bot.send_message(message.chat.id, response)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("/ADD"), types.KeyboardButton("/DELETE"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "/ADD")
def handle_add(message):
    # Prompt the user to send the name of the group to add
    bot.send_message(message.chat.id, "Please send the name of the coin to add : ")
    bot.register_next_step_handler(message, addNewGroup)


@bot.message_handler(func=lambda message: message.text == "/DELETE")
def handle_delete(message):
    grupn = returnGroups()
    response = "Select the number of the coin to delete:\n"
    response += "\n".join([f"{idx + 1}. {name}" for idx, name in enumerate(grupn)])
    bot.send_message(message.chat.id, response)
    # Next message from this user will be treated as their selection
    bot.register_next_step_handler(message, process_delete_selection)


def addNewGroup(message):
    txt = str(message.text)
    addtoDB(txt)
    bot.send_message(message.chat.id, f"Added {txt} Successfully!")
    show_options(message.chat.id)


def process_delete_selection(message):
    try:
        selection = int(message.text) - 1  # Convert user input into index
        groups = returnGroups()
        if selection >= 0 and selection < len(groups):
            group_to_delete = groups[selection]
            # Implement your deletion logic here, using group_to_delete
            bot.send_message(message.chat.id, f"Group '{group_to_delete}' has been deleted.")
            delgroup(group_to_delete)
            show_options(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Invalid selection. Please try again.")
            show_options(message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Please send a valid number.")


@bot.message_handler(func=lambda message: message.text == "Register")
def handle_register(message):
    user_id = message.from_user.id

    if user_id in logged_in_users:
        # User is already logged in, show options
        show_options(message.chat.id)
    else:
        # User is not logged in, proceed with registration
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Please enter your email address:", reply_markup=markup)
        bot.register_next_step_handler(message, register_user)


@bot.message_handler(func=lambda message: message.text == "/Logout")
def handle_option_4(message):
    user_id = message.from_user.id
    if user_id in logged_in_users:
        # User is logged in, log them out
        logout_user(user_id)
        bot.send_message(message.chat.id, "You have been successfully logged out.")
    else:
        # User is not logged in, show login/register options
        bot.send_message(message.chat.id, "You are not logged in. Choose an option:")

    # Show the login/register options
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Login")
    item2 = types.KeyboardButton("Register")
    markup.add(item1, item2)

    bot.send_message(message.chat.id, "Welcome! Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "/Crypto Analyse")
def analyze_coin(message):
    grupn = returnGroups()
    markup = types.InlineKeyboardMarkup(row_width=3)  # Set the desired row width here

    buttons = []  # List to hold all the buttons

    # Use emojis or special symbols to make buttons more attractive
    emoji_list = ["🚀", "💰", "🔔", "📈", "🌟"]  # Example emojis, add more if you have more groups

    # Iterate over the list of groups and create a button for each
    for idx, name in enumerate(grupn):
        # Append a different emoji to each group name for a stylish look
        emoji = emoji_list[idx % len(emoji_list)]  # Cycle through emojis if there are more groups than emojis
        button_text = f"{emoji} {name}"
        button = types.InlineKeyboardButton(text=button_text, callback_data=f"coin_{idx}")
        buttons.append(button)

    # Adding buttons to markup in rows of specified width
    while buttons:
        row = buttons[:3]  # Get the next row of buttons (up to 3 at a time)
        markup.add(*row)  # Unpack the row list into add()
        buttons = buttons[3:]  # Remove the added buttons from the list

    # Send a message with the inline keyboard
    bot.send_message(message.chat.id, "Select a group:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('coin_'))
def handle_coin_selection(call):
    group_index = int(call.data.split('_')[1])
    groups = returnGroups()
    selected_group = groups[group_index]

    # Send new buttons for analysis type
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Short Prediction", callback_data=f"short_{group_index}"))
    markup.add(types.InlineKeyboardButton(text="Long Prediction", callback_data=f"long_{group_index}"))
    markup.add(types.InlineKeyboardButton(text="Custom Prediction", callback_data=f"custom_{group_index}"))

    bot.send_message(call.message.chat.id, f"Selected {selected_group}. Choose analysis type:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(('short_', 'long_', 'custom_')))
def handle_analysis_selection(call):
    aiapi = get_user_aiapi(call.from_user.id)
    AIanalyze = aianalyz.ChatAnalysis(api_key=aiapi)
    analysis_type, group_index = call.data.split('_')[0], int(call.data.split('_')[1])
    groups = returnGroups()
    selected_group = groups[group_index]
    # Perform the analysis
    if analysis_type == "short":
        bot.answer_callback_query(call.id, f"Analyzing {selected_group} for a short term position!")
        curdata,orderbook = bnbot.fetch_historical_data(f"{selected_group}","1m","25 Mar 2024")
        result = AIanalyze.simpleAnalyze(curdata.tail(250),orderbook,bnbot.get_price(selected_group),value=selected_group)
        bot.send_message(call.message.chat.id, result)
    elif analysis_type == "long":
        bot.answer_callback_query(call.id, f"Analyzing { selected_group} for a long term position!")
        curdata,orderbook = bnbot.fetch_historical_data(f"{selected_group}","1h","1 Jan 2024")
        result = AIanalyze.LongTermAnalyze(curdata.tail(300),orderbook,bnbot.get_price(selected_group),value=selected_group)
        bot.send_message(call.message.chat.id, result)
    if analysis_type == "custom":
        # Inform the user to provide additional input
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Please enter custom command for the AI:")
        users_state[call.from_user.id] = "awaiting_custom_input"
        users_data[call.from_user.id] = {"group_index": selected_group}


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    if users_state.get(user_id) == "awaiting_time_interval":
        aiapi = get_user_aiapi(call.from_user.id)
        AIanalyze = aianalyz.ChatAnalysis(api_key=aiapi)
        interval = call.data
        selgroup = users_data[user_id].get("group_index")
        usrinput = users_data[user_id].get("custom_input")

        # Calculate "the day before"
        the_day_before = datetime.now() - timedelta(days=1)
        two_days_before = datetime.now() - timedelta(days=2)
        week_before = datetime.now() - timedelta(days=7)
        month_before = datetime.now() - timedelta(days=30)

        formatted_day_before = the_day_before.strftime("%d %b %Y")  # "DD Mon YYYY"
        formatted_two_days_before = two_days_before.strftime("%d %b %Y")
        formatted_week_before = week_before.strftime("%d %b %Y")
        formatted_month_before = month_before.strftime("%d %b %Y")
        if interval == "1m":
            currentdata,orderbook = bnbot.fetch_historical_data(f"{selgroup}", interval, formatted_day_before)
        elif interval == "5m":
            currentdata,orderbook = bnbot.fetch_historical_data(f"{selgroup}", interval, formatted_two_days_before)
        elif interval == "15m":
            currentdata,orderbook = bnbot.fetch_historical_data(f"{selgroup}", interval, formatted_week_before)
        elif interval == "1h":
            currentdata,orderbook = bnbot.fetch_historical_data(f"{selgroup}", interval, formatted_month_before)
        else:
            currentdata,orderbook = bnbot.fetch_historical_data(f"{selgroup}", interval, "1 Jan 2019")

        # Send the analyzed message
        bot.send_message(call.message.chat.id,
                         AIanalyze.customAnalyze(currentdata,orderbook,bnbot.get_price(selgroup), value=selgroup, cuscommand=usrinput))
        users_state[user_id] = None


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if users_state.get(user_id) == "awaiting_custom_input":
        group_index = users_data[user_id].get("group_index")
        process_custom_command(message, group_index)
        ask_time_interval(message)
        users_state[user_id] = "awaiting_time_interval"

def process_custom_command(message, group_index):
    input_text = message.text
    user_id = message.from_user.id
    # Store custom analysis input
    users_data[user_id]["custom_input"] = input_text

def ask_time_interval(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("1m", callback_data="1m"),
        types.InlineKeyboardButton("5m", callback_data="5m"),
        types.InlineKeyboardButton("15m", callback_data="15m")
    )
    keyboard.row(
        types.InlineKeyboardButton("1h", callback_data="1h"),
        types.InlineKeyboardButton("6h", callback_data="6h"),
        types.InlineKeyboardButton("1d", callback_data="1d")
    )
    bot.send_message(message.chat.id, "Please select a time interval:", reply_markup=keyboard)

def show_options(chat_id):
    options = ["/Crypto Analyse", "/EditDB", "/Logout"]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        markup.add(types.KeyboardButton(option))
    bot.send_message(chat_id, "Choose an option:", reply_markup=markup)

# Use environment variables for sensitive data
if __name__ == "__main__":
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Reconnecting in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before attempting to reconnect