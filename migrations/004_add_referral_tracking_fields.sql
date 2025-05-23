-- Migration to add advanced referral tracking columns
ALTER TABLE users ADD COLUMN referral_link TEXT;
ALTER TABLE users ADD COLUMN referral_tier INTEGER DEFAULT 0;