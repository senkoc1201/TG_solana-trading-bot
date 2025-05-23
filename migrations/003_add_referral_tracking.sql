-- Migration to add referral tracking columns to users table
ALTER TABLE users ADD COLUMN total_referrals INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN referral_rewards REAL DEFAULT 0.0;