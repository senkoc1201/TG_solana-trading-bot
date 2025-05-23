CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    referrer_id INTEGER,
    wallet_address TEXT,
    FOREIGN KEY (referrer_id) REFERENCES users(telegram_id)
);