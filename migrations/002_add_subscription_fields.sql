-- Migration to add subscription-related columns to users table
ALTER TABLE users ADD COLUMN subscription_type TEXT;
ALTER TABLE users ADD COLUMN subscription_start_date TIMESTAMP;
ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP;
ALTER TABLE users ADD COLUMN auto_renew BOOLEAN DEFAULT 0;