-- Migration to add bot wallet address tracking
ALTER TABLE users ADD COLUMN bot_wallet_address TEXT;