from datetime import datetime

from shared_resources import db

# Add new model for trade orders
class TradeOrder(db.Model):
    __tablename__ = 'trade_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.telegram_id'), nullable=False)
    wallet_address = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    trade_type = db.Column(db.String, nullable=False)  # 'buy' or 'sell'
    status = db.Column(db.String, default='open')  # 'open', 'completed', 'cancelled'
    transaction_signature = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)