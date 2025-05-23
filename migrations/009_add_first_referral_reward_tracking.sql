-- Migration to add tracking for first referral reward and paid referrals
ALTER TABLE users ADD COLUMN first_referral_reward_claimed BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN paid_referrals INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN total_paid_amount REAL DEFAULT 0.0;