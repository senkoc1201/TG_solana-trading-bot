-- Migration to add indexes for trade order queries
CREATE INDEX IF NOT EXISTS idx_trade_orders_user_id ON trade_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_orders_status ON trade_orders(status);
CREATE INDEX IF NOT EXISTS idx_trade_orders_token ON trade_orders(token);
CREATE INDEX IF NOT EXISTS idx_trade_orders_timestamp ON trade_orders(timestamp);