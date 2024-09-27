import os
from telegram import Update, ChatPermissions
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
from collections import defaultdict, deque

# Parameters
REPEAT_LIMIT = 5  # Number of repeated messages to trigger kick

# Dictionary to store user messages and repetitions
user_messages = defaultdict(lambda: deque(maxlen=REPEAT_LIMIT))

# Function to check for repeated messages
def check_repeated_messages(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    message_text = update.message.text

    # Log the received message
    print(f"Received message from user {user_id}: {message_text}")

    # Track the messages of the user
    user_history = user_messages[user_id]

    # Add the latest message to the user's history
    user_history.append(message_text)

    # If the same message is repeated enough times, kick the user
    if len(user_history) == REPEAT_LIMIT and len(set(user_history)) == 1:
        # Kick the user from the chat
        context.bot.kick_chat_member(chat_id=chat_id, user_id=user_id)

        # Notify the group
        update.message.reply_text(f"User {update.message.from_user.first_name} was kicked for spamming the same message.")

        # Clear the user's message history
        del user_messages[user_id]
    else:
        user_messages[user_id] = user_history

# Function to handle the /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I am the spam prevention bot. I'll kick users who send the same message repeatedly.")

def main():
    # Fetch the bot token from environment variables (set in Heroku Config Vars)
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    if TELEGRAM_TOKEN is None:
        raise ValueError("No Telegram bot token provided. Please set TELEGRAM_TOKEN environment variable.")

    # Initialize the Updater and Dispatcher
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add /start command handler
    dp.add_handler(CommandHandler("start", start))

    # Add handler for text messages to check for repeated messages (in groups)
    dp.add_handler(MessageHandler(Filters.text & Filters.group, check_repeated_messages))

    # Start the bot and begin polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
