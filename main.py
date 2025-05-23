import time
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from models import db, User
from abilities import apply_sqlite_migrations
from shared_resources import app
from commands import (
    trade_command, sell_command, buy_command,
    autopay_command, subscribe_command
)

from utils import print_setup_instructions
import os
import logging
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from models import db, User
from abilities import apply_sqlite_migrations

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import Flask app
from shared_resources import app
db.init_app(app)

def register_user(telegram_id: int, username: str, referrer_id: int = None) -> User:
    """Register a new user or return existing one."""
    with app.app_context():
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                referrer_id=referrer_id
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {username} (ID: {telegram_id})")
        return user

def start(update: Update, context: CallbackContext) -> None:
    """Handle the /start command with enhanced referral tracking."""
    user = update.effective_user
    referrer_id = None
    
    # Check for referral code
    if context.args and context.args[0].startswith('ref_'):
        try:
            referrer_id = int(context.args[0][4:])  # Extract ID from 'ref_123456'
        except ValueError:
            logger.warning(f"Invalid referral code: {context.args[0]}")
    
    # Register user
    registered_user = register_user(user.id, user.username, referrer_id)
    
    # Update referrer's stats if a valid referrer exists
    if referrer_id:
        with app.app_context():
            referrer = User.query.filter_by(telegram_id=referrer_id).first()
            if referrer:
                # Increment total referrals
                referrer.total_referrals += 1
                
                # Implement tiered referral rewards
                base_reward = 5.00  # Base reward amount
                tier_multipliers = {0: 1.0, 1: 1.1, 2: 1.15, 3: 1.2}
                current_tier = min(referrer.referral_tier, 3)
                
                # Calculate and add referral rewards with more precise tracking
                referral_reward = base_reward * tier_multipliers[current_tier]
                referrer.referral_rewards += referral_reward
                
                # Implement advanced referral tier system
                if referrer.total_referrals % 100 == 0:
                    referrer.referral_tier = min(referrer.referral_tier + 1, 3)
                    logger.info(
                        f"User {referrer.username} advanced to referral tier {referrer.referral_tier}. "
                        f"Total referrals: {referrer.total_referrals}"
                    )
                
                # Log referral event for tracking
                logger.info(
                    f"Referral tracked: Referrer {referrer.username} (ID: {referrer.telegram_id}), "
                    f"Reward: ${referral_reward:.2f}, Tier: {current_tier}"
                )
                
                # Update referrer's tier multiplier
                referrer.referral_tier_multiplier = tier_multipliers[current_tier]
                
                db.session.commit()
    
    # Prepare welcome message
    welcome_msg = f"Hi {user.first_name}! Welcome to the Solana Trading Bot!\n\n"
    
    if referrer_id:
        welcome_msg += f"You were referred by user {referrer.username}. You'll both earn rewards on your transactions!\n\n"
    
    welcome_msg += "🔑 Please set up your Solana wallet using the /wallet command before making any transactions.\n\n"
    welcome_msg += "Use /help to see all available commands."
    
    update.message.reply_text(welcome_msg)

def is_valid_solana_wallet_address(address: str) -> bool:
    """Validate Solana wallet address."""
    # Basic Solana address validation
    # Solana addresses are base58 encoded and typically 32-44 characters long
    # They usually start with 1, 2, 3, or 4
    if not address:
        return False
    
    # Check length (Solana addresses are typically 32-44 characters)
    if len(address) < 32 or len(address) > 44:
        return False
    
    # Check first character (Solana addresses start with 1, 2, 3, or 4)
    if address[0] not in '1234':
        return False
    
    # Check if address contains only base58 characters
    base58_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    if not all(char in base58_chars for char in address):
        return False
    
    return True

def wallet_command(update: Update, context: CallbackContext) -> None:
    """Handle the /wallet command."""
    user = update.effective_user
    
    with app.app_context():
        db_user = User.query.filter_by(telegram_id=user.id).first()
        
        if not db_user:
            update.message.reply_text("Please start the bot first with /start")
            return
        
        # If no arguments provided, show current wallet
        if not context.args:
            if db_user.wallet_address:
                update.message.reply_text(f"Your current Solana wallet address is:\n{db_user.wallet_address}")
            else:
                update.message.reply_text("You haven't set a wallet address yet.\nUse /wallet <address> to set your Solana wallet address.")
            return
        
        # Update wallet address
        new_address = context.args[0]
        
        # Validate Solana wallet address
        if not is_valid_solana_wallet_address(new_address):
            update.message.reply_text("❌ Invalid Solana wallet address. Please check and try again.\n\n"
                                      "A valid Solana wallet address:\n"
                                      "- Is 32-44 characters long\n"
                                      "- Starts with 1, 2, 3, or 4\n"
                                      "- Contains only base58 characters")
            return
        
        db_user.wallet_address = new_address
        db.session.commit()
        update.message.reply_text(f"✅ Your Solana wallet address has been updated to:\n{new_address}")

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🤖 Solana Trading Bot Commands 🤖

💰 Subscription Commands:
/subscribe - View and purchase subscription plans:
  • $5/week (auto-renewed)
  • $1000/year (one-time payment)
/status - Check your subscription status and remaining time
/autopay on/off - Enable/disable weekly auto-renewal

👛 Wallet Management:
/wallet [address] - Set or view your Solana wallet address

🤝 Referral Program:
/referral - Get your unique referral link and track rewards
  • 100% reward on first referral's payment
  • 30% ongoing referral rewards
  • +10% bonus for every 100 paid users
  • Rewards paid directly in SOL

💹 Trading Commands:
/buy - Initiate a buy transaction
/sell - Initiate a sell transaction  
/trade - Start a peer-to-peer trade

🆘 Other Commands:
/start - Start the bot and register
/help - Show this help message

💡 How to Subscribe:
1. Set your wallet address using /wallet
2. View plans with /subscribe
3. Send SOL to bot's wallet
4. Subscription activates automatically
"""
    update.message.reply_text(help_text)

def plans_command(update: Update, context: CallbackContext) -> None:
    """Display available subscription plans."""
    plans_text = """
🚀 Solana Trading Bot Subscription Plans 🚀

1️⃣ Weekly Plan: $5/week
   - Auto-renewed weekly
   - Continuous access to trading signals
   - Instant cancellation possible

2️⃣ Annual Plan: $1000/year
   - One-time payment
   - Best value for long-term traders
   - Full year of premium features

💰 How to Activate:
- Send SOL to our bot's wallet address
- Wallet-to-wallet payment confirms your subscription
- Referral discounts available!
"""
    update.message.reply_text(plans_text)

def status_command(update: Update, context: CallbackContext) -> None:
    """Check user's current subscription status."""
    user = update.effective_user
    
    with app.app_context():
        db_user = User.query.filter_by(telegram_id=user.id).first()
        
        if not db_user:
            update.message.reply_text("Please start the bot first with /start")
            return
        
        if not db_user.subscription_type:
            update.message.reply_text("You currently have no active subscription. Use /plans to view available plans.")
            return
        
        status_text = f"📊 Subscription Status:\n"
        status_text += f"Plan: {db_user.subscription_type.capitalize()} Plan\n"
        
        if db_user.subscription_end_date:
            from datetime import datetime
            remaining_time = db_user.subscription_end_date - datetime.now()
            days = remaining_time.days
            hours = remaining_time.seconds // 3600
            
            status_text += f"Expires in: {days} days, {hours} hours\n"
        
        status_text += f"Auto-Renew: {'Enabled' if db_user.auto_renew else 'Disabled'}"
        
        update.message.reply_text(status_text)

def referrals_command(update: Update, context: CallbackContext) -> None:
    """Show user's referral statistics and generate referral link."""
    user = update.effective_user
    
    with app.app_context():
        db_user = User.query.filter_by(telegram_id=user.id).first()
        
        if not db_user:
            update.message.reply_text("Please start the bot first with /start")
            return
        
        # Generate or retrieve referral link
        if not db_user.referral_link:
            # Use utility function to get bot username
            from utils import get_bot_username
            bot_username = get_bot_username() or 'solana_trading_bot'
            db_user.referral_link = f"https://t.me/{bot_username}?start=ref_{db_user.telegram_id}"
            db.session.commit()
        
        # Calculate potential next tier and rewards
        next_tier_threshold = (db_user.referral_tier + 1) * 100
        referrals_to_next_tier = max(0, next_tier_threshold - db_user.total_referrals)
        
        # Calculate potential rewards with more precise calculation
        tier_multipliers = {0: 1.0, 1: 1.1, 2: 1.15, 3: 1.2}
        base_reward_percentage = 0.05  # 5% base referral reward
        current_tier = min(db_user.referral_tier, 3)
        potential_rewards = (
            db_user.total_referrals * 
            base_reward_percentage * 
            db_user.referral_tier_multiplier
        )
        
        referral_text = f"🤝 Your Referral Stats:\n"
        referral_text += f"Total Referrals: {db_user.total_referrals}\n"
        referral_text += f"Potential Referral Rewards: ${potential_rewards:.2f}\n"
        referral_text += f"Current Referral Tier: {db_user.referral_tier}\n"
        referral_text += f"Next Tier Progress: {db_user.total_referrals}/{next_tier_threshold} referrals\n"
        referral_text += f"Referrals needed for next tier: {referrals_to_next_tier}\n\n"
        referral_text += "📋 Share this link to earn rewards:\n"
        referral_text += f"{db_user.referral_link}\n\n"
        referral_text += "🏆 Referral Tier Benefits:\n"
        referral_text += "- Tier 0: 5% referral rewards\n"
        referral_text += "- Tier 1: 10% referral rewards\n"
        referral_text += "- Tier 2: 15% referral rewards\n"
        referral_text += "- Tier 3: 20% referral rewards\n"
        
        update.message.reply_text(referral_text)

def setup_telegram_bot():
    if not TELEGRAM_API_TOKEN:
        logger.error("TELEGRAM_API_TOKEN is missing. Please set it in the Env Secrets tab.")
        print_setup_instructions()
        return False

    try:
        updater = Updater(TELEGRAM_API_TOKEN)
        dispatcher = updater.dispatcher

        # Add command handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("wallet", wallet_command))
        dispatcher.add_handler(CommandHandler("subscribe", subscribe_command))
        dispatcher.add_handler(CommandHandler("status", status_command))
        dispatcher.add_handler(CommandHandler("referral", referrals_command))
        dispatcher.add_handler(CommandHandler("autopay", autopay_command))
        dispatcher.add_handler(CommandHandler("buy", buy_command))
        dispatcher.add_handler(CommandHandler("sell", sell_command))
        dispatcher.add_handler(CommandHandler("trade", trade_command))
        
        logger.info("Bot has been set up successfully.")
        return updater
    except Exception as e:
        logger.error(f"Failed to set up Telegram bot: {str(e)}")
        return False

def run_telegram_bot(updater):
    logger.info("Starting Telegram bot")
    updater.start_polling()
    logger.info("Bot is now running.")
    print("🎉 Bot is now connected and ready to use! 🎉")
    print(f"🚀 Click here to start chatting: https://t.me/{updater.bot.username} 🚀")

from blockchain_monitor import monitor_blockchain_payments
import threading

def periodic_blockchain_check():
    """Run blockchain payment monitoring periodically."""
    while True:
        try:
            monitor_blockchain_payments()
        except Exception as e:
            logger.error(f"Error in periodic blockchain check: {str(e)}")
        
        # Check every hour
        time.sleep(3600)

def main():
    # Initialize database
    with app.app_context():
        apply_sqlite_migrations(db.engine, db.Model, "migrations")

    # Set up the Telegram bot
    updater = setup_telegram_bot()
    if not updater:
        logger.error("Failed to set up Telegram bot. Exiting.")
        return

    # Start blockchain monitoring in a separate thread
    blockchain_thread = threading.Thread(target=periodic_blockchain_check, daemon=True)
    blockchain_thread.start()

    # Start the Telegram bot
    run_telegram_bot(updater)

if __name__ == "__main__":
    main()