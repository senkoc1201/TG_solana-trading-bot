-- Migration to create trade_orders table
CREATE TABLE IF NOT EXISTS trade_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    wallet_address TEXT NOT NULL,
    token TEXT NOT NULL,
    amount REAL NOT NULL,
    price REAL NOT NULL,
    trade_type TEXT NOT NULL,
   status TEXT DEFAULT 'open',
   transaction_signature TEXT,
   timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (user_id) REFERENCES users(telegram_id)
);