-- Migration to add Solana RPC endpoint configuration
ALTER TABLE users ADD COLUMN solana_rpc_endpoint TEXT;