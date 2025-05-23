# Solana Trading Bot 🤖

A Telegram-based trading bot for Solana blockchain that enables users to perform trades, manage subscriptions, and participate in a referral program.

## Features 🌟

### Trading Capabilities
- Execute buy and sell transactions on Solana blockchain
- Peer-to-peer trading functionality
- Real-time blockchain monitoring
- Secure wallet management

### Subscription System
- Weekly subscription ($5/week) with auto-renewal
- Annual subscription ($1000/year) one-time payment
- Subscription status tracking
- Auto-payment management

### Referral Program
- Multi-tiered referral rewards system
- Base reward of $5.00 per referral
- Tier multipliers:
  - Tier 0: 1.0x
  - Tier 1: 1.1x
  - Tier 2: 1.15x
  - Tier 3: 1.2x
- Automatic tier advancement every 100 referrals
- Direct SOL rewards distribution

## Prerequisites 📋

- Python 3.7+
- Telegram Bot Token
- Solana wallet
- SQLite database

## Installation 🚀

1. Clone the repository:
```bash
git clone [repository-url]
cd solana-trading-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export TELEGRAM_API_TOKEN='your-telegram-bot-token'
```

4. Initialize the database:
```bash
python app_init.py
```

## Usage 💡

### Bot Commands

#### Basic Commands
- `/start` - Start the bot and register
- `/help` - Display all available commands
- `/wallet [address]` - Set or view your Solana wallet address

#### Trading Commands
- `/buy` - Initiate a buy transaction
- `/sell` - Initiate a sell transaction
- `/trade` - Start a peer-to-peer trade

#### Subscription Commands
- `/subscribe` - View and purchase subscription plans
- `/status` - Check subscription status
- `/autopay on/off` - Toggle auto-renewal

#### Referral Commands
- `/referral` - Get your unique referral link and track rewards

## Project Structure 📁

- `main.py` - Core bot functionality and command handlers
- `blockchain_monitor.py` - Blockchain monitoring and transaction processing
- `commands.py` - Command implementations
- `models.py` - Database models
- `utils.py` - Utility functions
- `shared_resources.py` - Shared resources and configurations
- `requirements.txt` - Project dependencies

## Security 🔒

- Wallet address validation
- Secure transaction processing
- Protected API endpoints
- Database encryption

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

For support, please open an issue in the repository or contact the development team. 
