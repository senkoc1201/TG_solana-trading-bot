-- Migration to add trading method tracking
ALTER TABLE users ADD COLUMN trading_method TEXT;