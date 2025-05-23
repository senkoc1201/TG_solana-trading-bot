-- Migration to enhance user model with new fields
ALTER TABLE users ADD COLUMN last_payment_date TIMESTAMP;
ALTER TABLE users ADD COLUMN last_payment_amount REAL DEFAULT 0.0;
ALTER TABLE users ADD COLUMN pending_rewards REAL DEFAULT 0.0;
ALTER TABLE users ADD COLUMN is_trading_enabled BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN last_trade_date TIMESTAMP;
ALTER TABLE users ADD COLUMN total_trades INTEGER DEFAULT 0;