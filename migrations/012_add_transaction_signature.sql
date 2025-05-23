-- Migration to add transaction signature tracking
ALTER TABLE users ADD COLUMN last_transaction_signature TEXT;