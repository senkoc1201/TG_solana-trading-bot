-- Migration to enhance referral tracking system
ALTER TABLE users ADD COLUMN referral_tier_multiplier REAL DEFAULT 1.0;