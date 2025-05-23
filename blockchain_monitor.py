import logging
import os
from datetime import datetime, timedelta
from shared_resources import db, app
from models import User
from sqlalchemy import func

logger = logging.getLogger(__name__)

def get_bot_wallet_address():
    """Retrieve bot's Solana wallet address from environment variables."""
    return os.getenv('BOT_SOLANA_WALLET_ADDRESS')

import requests
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
import asyncio

async def verify_blockchain_payment(transaction_details):
    """
    Verify blockchain payment details using Solana RPC.
    
    Args:
        transaction_details (dict): Details of the blockchain transaction
    
    Returns:
        bool: Whether the payment is valid
    """
    try:
        # Use environment variable for Solana RPC endpoint
        solana_rpc_url = os.getenv('SOLANA_RPC_ENDPOINT', 'https://api.mainnet-beta.solana.com')
        client = AsyncClient(solana_rpc_url)
        
        # Validate transaction details
        if not all(key in transaction_details for key in ['from_address', 'to_address', 'amount']):
            logger.warning("Incomplete transaction details")
            return False
        
        # Check transaction to bot's wallet
        bot_wallet = get_bot_wallet_address()
        if transaction_details['to_address'] != bot_wallet:
            logger.warning(f"Transaction not to bot wallet: {transaction_details['to_address']}")
            return False
        
        # Validate transaction amount
        if transaction_details['amount'] not in [5.0, 1000.0]:
            logger.warning(f"Invalid payment amount: {transaction_details['amount']}")
            return False
        
        # Additional Solana-specific transaction verification
        # Check network connectivity
        if not await client.is_connected():
            logger.warning("Unable to connect to Solana network")
            return False
        
        # Verify transaction signature and status
        transaction_signature = transaction_details.get('transaction_signature')
        if transaction_signature:
            try:
                transaction_status = await client.get_transaction(transaction_signature)
                if not transaction_status or transaction_status.get('status') != 'Success':
                    logger.warning("Transaction verification failed")
                    return False
            except Exception as e:
                logger.error(f"Transaction signature verification error: {str(e)}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Blockchain payment verification error: {str(e)}")
        return False

def process_subscription_payment(user, payment_amount):
    """
    Process subscription payment for a user.
    
    Args:
        user (User): User object
        payment_amount (float): Amount paid in SOL
    """
    with app.app_context():
        current_time = datetime.utcnow()
        
        # Determine subscription type based on payment
        if payment_amount == 5.0:  # Weekly plan
            user.subscription_type = 'weekly'
            user.subscription_start_date = current_time
            user.subscription_end_date = current_time + timedelta(days=7)
        elif payment_amount == 1000.0:  # Annual plan
            user.subscription_type = 'annual'
            user.subscription_start_date = current_time
            user.subscription_end_date = current_time + timedelta(days=365)
        
        user.last_payment_date = current_time
        user.last_payment_amount = payment_amount
        user.total_paid_amount += payment_amount
        
        db.session.commit()

def process_referral_rewards(user, payment_amount):
    """
    Process referral rewards for a user's referrer.
    
    Args:
        user (User): User who made the payment
        payment_amount (float): Amount paid in SOL
    """
    with app.app_context():
        referrer = User.query.filter_by(telegram_id=user.referrer_id).first()
        
        if referrer:
            reward_percentage = referrer.calculate_referral_reward_percentage()
            referral_reward = payment_amount * (reward_percentage / 100)
            
            # Track first referral reward
            if not referrer.first_referral_reward_claimed:
                referrer.first_referral_reward_claimed = True
                referrer.referral_rewards += referral_reward * 2  # 100% reward
            else:
                referrer.referral_rewards += referral_reward
            
            referrer.paid_referrals += 1
            
            # Update referral tier
            if referrer.paid_referrals % 100 == 0:
                referrer.referral_tier = min(referrer.referral_tier + 1, 3)
            
            db.session.commit()

async def monitor_blockchain_payments():
    """
    Background service to monitor Solana blockchain for payments
    - Check for new payments to bot's wallet
    - Verify and process subscriptions
    - Distribute referral rewards
    """
    try:
        # TODO: Replace with actual Solana blockchain transaction retrieval
        # This is a placeholder for blockchain payment monitoring
        with app.app_context():
            # Find users with pending subscriptions
            users_to_check = User.query.filter(
                User.wallet_address.isnot(None),
                User.subscription_end_date.is_(None) | (User.subscription_end_date < datetime.utcnow())
            ).all()
            
            for user in users_to_check:
                # Simulate blockchain payment check
                transaction_details = {
                    'from_address': user.wallet_address,
                    'to_address': get_bot_wallet_address(),
                    'amount': 5.0  # Simulated weekly payment
                }
                
                if await verify_blockchain_payment(transaction_details):
                    process_subscription_payment(user, transaction_details['amount'])
                    process_referral_rewards(user, transaction_details['amount'])
                    
                    logger.info(f"Processed payment for user {user.username}")
    
    except Exception as e:
        logger.error(f"Error in blockchain payment monitoring: {str(e)}")

def run_monitoring():
    asyncio.run(monitor_blockchain_payments())