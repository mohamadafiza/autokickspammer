from telegram import Update, ChatPermissions
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
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

def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    updater = Updater("7694147971:AAGD5CgomNFAX_sBQ6eC7U9HXVXfj6rvVgU", use_context=True)
    dp = updater.dispatcher

    # Handler for text messages
    dp.add_handler(MessageHandler(Filters.text & Filters.group, check_repeated_messages))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()