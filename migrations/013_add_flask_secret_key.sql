-- Migration to add Flask secret key configuration
ALTER TABLE users ADD COLUMN flask_secret_key TEXT;