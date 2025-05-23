from blockchain_monitor import AsyncClient

from shared_resources import os

from blockchain_monitor import datetime

from shared_resources import app

from telegram import Update
from telegram.ext import CallbackContext
from models import db, User
import logging

logger = logging.getLogger(__name__)

def subscribe_command(update: Update, context: CallbackContext) -> None:
    """Handle the /subscribe command."""
    subscription_text = """
💰 Available Subscription Plans:

1️⃣ Weekly Plan - $5/week
   • Auto-renewable subscription
   • Full access to trading features
   • Cancel anytime

2️⃣ Annual Plan - $1000/year
   • One-time payment
   • Full access for 12 months
   • Best value for long-term traders

To subscribe:
1. Ensure your wallet is set (/wallet)
2. Send payment to bot's wallet:
   <BOT_WALLET_ADDRESS>

Your subscription will activate automatically
once payment is confirmed on-chain.
"""
    update.message.reply_text(subscription_text)

def autopay_command(update: Update, context: CallbackContext) -> None:
    """Handle the /autopay command."""
    user = update.effective_user
    
    if not context.args:
        update.message.reply_text("Usage: /autopay on - Enable auto-renewal\n"
                                 "       /autopay off - Disable auto-renewal")
        return
    
    setting = context.args[0].lower()
    if setting not in ['on', 'off']:
        update.message.reply_text("Invalid option. Use 'on' or 'off'.")
        return
    
    with app.app_context():
        db_user = User.query.filter_by(telegram_id=user.id).first()
        if not db_user:
            update.message.reply_text("Please start the bot first with /start")
            return
        
        if not db_user.wallet_address:
            update.message.reply_text("Please set your wallet first using /wallet")
            return
        
        db_user.auto_renew = (setting == 'on')
        db.session.commit()
        
        status = "enabled" if setting == 'on' else "disabled"
        update.message.reply_text(f"Auto-renewal has been {status}.")

def buy_command(update: Update, context: CallbackContext) -> None:
    """Handle the /buy command for executing buy transactions."""
    user = update.effective_user
    
    # Validate command arguments
    if not context.args or len(context.args) != 2:
        update.message.reply_text(
            "Usage: /buy <token_symbol> <amount>\n"
            "Example: /buy SOL 0.5"
        )
        return
    
    token_symbol = context.args[0].upper()
    try:
        amount = float(context.args[1])
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        update.message.reply_text("Invalid amount. Please enter a positive number.")
        return
    
    with app.app_context():
        db_user = User.query.filter_by(telegram_id=user.id).first()
        
        # Check if user is authenticated and has a wallet
        if not db_user or not db_user.wallet_address:
            update.message.reply_text("Please set up your wallet first using /wallet command.")
            return
        
        # Check if user has an active subscription
        if not db_user.is_subscription_active():
            update.message.reply_text("You need an active subscription to use trading features. Use /subscribe to activate.")
            return
        
        try:
            # Connect to Solana blockchain
            solana_rpc_url = os.getenv('SOLANA_RPC_ENDPOINT')
            client = AsyncClient(solana_rpc_url)
            
            # Validate wallet balance
            wallet_balance = await client.get_balance(db_user.wallet_address)
            if wallet_balance < amount:
                update.message.reply_text(f"❌ Insufficient balance. Current balance: {wallet_balance} SOL")
                return
            
            # Prepare transaction
            transaction = Transaction().add(
                client.transfer(
                    from_pubkey=db_user.wallet_address, 
                    to_pubkey=os.getenv('BOT_SOLANA_WALLET_ADDRESS'),
                    lamports=int(amount * 1_000_000_000)  # Convert SOL to lamports
                )
            )
            
            # Sign and send transaction
            try:
                signature = await client.send_transaction(transaction)
                
                # Verify transaction
                transaction_details = {
                    'from_address': db_user.wallet_address,
                    'to_address': os.getenv('BOT_SOLANA_WALLET_ADDRESS'),
                    'amount': amount,
                    'transaction_signature': signature
                }
                
                # Verify blockchain payment
                from blockchain_monitor import verify_blockchain_payment
                is_valid = await verify_blockchain_payment(transaction_details)
                
                if is_valid:
                    # Update user's trading stats
                    db_user.total_trades += 1
                    db_user.last_trade_date = datetime.utcnow()
                    db_user.is_trading_enabled = True
                    db_user.last_transaction_signature = signature
                    db.session.commit()
                    
                    update.message.reply_text(
                        f"📈 Buy order executed successfully!\n"
                        f"Token: {token_symbol}\n"
                        f"Amount: {amount} SOL\n"
                        f"Transaction Signature: {signature}"
                    )
                else:
                    update.message.reply_text("❌ Transaction verification failed.")
                    
            except Exception as e:
                logger.error(f"Buy transaction failed: {str(e)}")
                update.message.reply_text("❌ Failed to execute buy order. Please try again later.")
                
        except Exception as e:
            logger.error(f"Error connecting to blockchain: {str(e)}")
            update.message.reply_text("❌ Failed to connect to blockchain. Please try again later.")
def sell_command(update: Update, context: CallbackContext) -> None:
    """Handle the /sell command for executing sell transactions."""
    user = update.effective_user
    
    # Validate command arguments
    if not context.args or len(context.args) != 2:
        update.message.reply_text(
            "Usage: /sell <token_symbol> <amount>\n"
            "Example: /sell SOL 0.5"
        )
        return
    
    token_symbol = context.args[0].upper()
    try:
        amount = float(context.args[1])
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        update.message.reply_text("Invalid amount. Please enter a positive number.")
        return
    
    with app.app_context():
        db_user = User.query.filter_by(telegram_id=user.id).first()
        
        # Check if user is authenticated and has a wallet
        if not db_user or not db_user.wallet_address:
            update.message.reply_text("Please set up your wallet first using /wallet command.")
            return
        
        # Check if user has an active subscription
        if not db_user.is_subscription_active():
            update.message.reply_text("You need an active subscription to use trading features. Use /subscribe to activate.")
            return
        
        try:
            # Connect to Solana blockchain
            solana_rpc_url = os.getenv('SOLANA_RPC_ENDPOINT')
            client = AsyncClient(solana_rpc_url)
            
            # Validate wallet balance
            wallet_balance = await client.get_balance(db_user.wallet_address)
            if wallet_balance < amount:
                update.message.reply_text(f"❌ Insufficient balance. Current balance: {wallet_balance} SOL")
                return
            
            # Prepare transaction
            transaction = Transaction().add(
                client.transfer(
                    from_pubkey=db_user.wallet_address, 
                    to_pubkey=os.getenv('BOT_SOLANA_WALLET_ADDRESS'),
                    lamports=int(amount * 1_000_000_000)  # Convert SOL to lamports
                )
            )
            
            # Sign and send transaction
            try:
                signature = await client.send_transaction(transaction)
                
                # Verify transaction
                transaction_details = {
                    'from_address': db_user.wallet_address,
                    'to_address': os.getenv('BOT_SOLANA_WALLET_ADDRESS'),
                    'amount': amount,
                    'transaction_signature': signature
                }
                
                # Verify blockchain payment
                from blockchain_monitor import verify_blockchain_payment
                is_valid = await verify_blockchain_payment(transaction_details)
                
                if is_valid:
                    # Update user's trading stats
                    db_user.total_trades += 1
                    db_user.last_trade_date = datetime.utcnow()
                    db_user.is_trading_enabled = True
                    db_user.last_transaction_signature = signature
                    db.session.commit()
                    
                    update.message.reply_text(
                        f"📉 Sell order executed successfully!\n"
                        f"Token: {token_symbol}\n"
                        f"Amount: {amount} SOL\n"
                        f"Transaction Signature: {signature}"
                    )
                else:
                    update.message.reply_text("❌ Transaction verification failed.")
                    
def trade_command(update: Update, context: CallbackContext) -> None:
    """Handle the /trade command for P2P trading."""
    user = update.effective_user
    
    # Validate command arguments
    if not context.args or len(context.args) != 4:
        update.message.reply_text(
            "Usage: /trade <token_symbol> <amount> <price> <trade_type>\n"
            "Example: /trade SOL 0.5 50 buy\n"
            "Trade types: buy, sell"
        )
        return
    
    token_symbol = context.args[0].upper()
    try:
        amount = float(context.args[1])
        price = float(context.args[2])
        if amount <= 0 or price <= 0:
            raise ValueError("Amount and price must be positive")
    except ValueError:
        update.message.reply_text("Invalid amount or price. Please enter positive numbers.")
        return
    
    trade_type = context.args[3].lower()
    if trade_type not in ['buy', 'sell']:
        update.message.reply_text("Invalid trade type. Use 'buy' or 'sell'.")
        return
    
    with app.app_context():
        db_user = User.query.filter_by(telegram_id=user.id).first()
        
        # Check if user is authenticated and has a wallet
        if not db_user or not db_user.wallet_address:
            update.message.reply_text("Please set up your wallet first using /wallet command.")
            return
        
        # Check if user has an active subscription
        if not db_user.is_subscription_active():
            update.message.reply_text("You need an active subscription to use trading features. Use /subscribe to activate.")
            return
        
        try:
            # Create P2P trade order
            order = {
                'user_id': db_user.telegram_id,
                'wallet_address': db_user.wallet_address,
                'token': token_symbol,
                'amount': amount,
                'price': price,
                'type': trade_type,
                'timestamp': datetime.utcnow()
            }
            
            # Validate wallet balance for trade
            solana_rpc_url = os.getenv('SOLANA_RPC_ENDPOINT')
            client = AsyncClient(solana_rpc_url)
            wallet_balance = await client.get_balance(db_user.wallet_address)
            
            if wallet_balance < amount * price:
                update.message.reply_text(f"❌ Insufficient balance. Current balance: {wallet_balance} SOL")
                return
            
            # Store trade order in database
            trade_order = TradeOrder(
                user_id=db_user.telegram_id,
                wallet_address=db_user.wallet_address,
                token=token_symbol,
                amount=amount,
                price=price,
                trade_type=trade_type,
                status='open'
            )
            db.session.add(trade_order)
            db.session.commit()
            
            # Prepare transaction for potential immediate execution
            transaction = Transaction().add(
                client.transfer(
                    from_pubkey=db_user.wallet_address, 
                    to_pubkey=os.getenv('BOT_SOLANA_WALLET_ADDRESS'),
                    lamports=int(amount * price * 1_000_000_000)  # Convert SOL to lamports
                )
            )
            
            try:
                signature = await client.send_transaction(transaction)
                
                # Verify transaction
                transaction_details = {
                    'from_address': db_user.wallet_address,
                    'to_address': os.getenv('BOT_SOLANA_WALLET_ADDRESS'),
                    'amount': amount * price,
                    'transaction_signature': signature
                }
                
                # Verify blockchain payment
                from blockchain_monitor import verify_blockchain_payment
                is_valid = await verify_blockchain_payment(transaction_details)
                
                if is_valid:
                    # Update trade order status
                    trade_order.status = 'completed'
                    trade_order.transaction_signature = signature
                    
                    # Update user's trading stats
                    db_user.total_trades += 1
                    db_user.last_trade_date = datetime.utcnow()
                    db_user.is_trading_enabled = True
                    db_user.last_transaction_signature = signature
                    db.session.commit()
                    
                    update.message.reply_text(
                        f"🤝 P2P Trade Order Executed!\n"
                        f"Token: {token_symbol}\n"
                        f"Amount: {amount}\n"
                        f"Price: ${price}\n"
                        f"Type: {trade_type.upper()}\n"
                        f"Transaction Signature: {signature}"
                    )
                else:
                    update.message.reply_text("❌ Trade order verification failed.")
            except Exception as e:
                logger.error(f"P2P trade execution failed: {str(e)}")
                update.message.reply_text("❌ Failed to execute trade order. Please try again later.")
        except Exception as e:
            logger.error(f"Error connecting to blockchain: {str(e)}")
            update.message.reply_text("❌ Failed to connect to blockchain. Please try again later.")