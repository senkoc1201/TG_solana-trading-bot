-- Migration to enhance referral tracking system
-- First check if column exists to avoid errors
CREATE TABLE IF NOT EXISTS users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    referrer_id INTEGER,
    wallet_address TEXT,
    subscription_type TEXT,
    subscription_start_date TIMESTAMP,
    subscription_end_date TIMESTAMP,
    auto_renew BOOLEAN DEFAULT 0,
    total_referrals INTEGER DEFAULT 0,
    referral_rewards REAL DEFAULT 0.0,
    referral_link TEXT,
    referral_tier INTEGER DEFAULT 0,
    referral_tier_multiplier REAL DEFAULT 1.0,
    FOREIGN KEY (referrer_id) REFERENCES users(telegram_id)
);

-- Copy data from old table
INSERT INTO users_new 
SELECT 
    id,
    telegram_id,
    username,
    registration_date,
    referrer_id,
    wallet_address,
    subscription_type,
    subscription_start_date,
    subscription_end_date,
    auto_renew,
    total_referrals,
    referral_rewards,
    referral_link,
    referral_tier,
    1.0 as referral_tier_multiplier
FROM users;

-- Drop old table
DROP TABLE users;

-- Rename new table
ALTER TABLE users_new RENAME TO users;