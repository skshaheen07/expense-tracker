from datetime import datetime

from models import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    type = db.Column(
        db.String(20),
        nullable=False
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    date = db.Column(
        db.Date,
        default=datetime.utcnow
    )

    notes = db.Column(
        db.Text
    )

    def __repr__(self):
        return f"<Transaction {self.title}>"