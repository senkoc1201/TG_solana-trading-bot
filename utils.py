import os
import telegram
import logging

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
logger = logging.getLogger(__name__)

bot_username = None

def get_bot_username():
    global bot_username
    if bot_username is None:
        try:
            bot = telegram.Bot(token=TELEGRAM_API_TOKEN)
            bot_username = bot.get_me().username
        except Exception as e:
            logger.error(f"Failed to get bot username: {str(e)}, did you setup a correct telegram API key?")
    return bot_username

def print_setup_instructions():
    print("🤖 Welcome to the Telegram Bot Setup! 🤖")
    print("\n🔑 Here's how to get started:")
    print("1️⃣ Get a Telegram bot API key:")
    print("   👉 Click this link to message BotFather: https://t.me/BotFather and type /newbot")
    print("   👉 Follow the prompts to create your new bot")
    print("   👉 BotFather will give you an API key for your new bot")
    print("\n2️⃣ Set up your bot:")
    print("   👉 Copy the API key from BotFather")
    print("   👉 Paste it into the Env Secrets tab in the Lazy Builder")
    print("   👉 Look for the TELEGRAM_API_TOKEN secret and fill it in")
    print("\n3️⃣ Launch your bot:")
    print("   👉 Run your Lazy app again")
    print("   👉 Your bot will come online! 🎉")
    print("\n🌟 Good luck with your new Telegram bot! 🌟")
    
    pass