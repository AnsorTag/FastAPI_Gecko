from sqlalchemy.orm import Session
from app.models.model import Transaction


# Create
def create_transaction(db: Session, crypto_name: str, amount: float, price_usd: float):
    db_transaction = Transaction(
        crypto_name=crypto_name, amount=amount, price_usd=price_usd
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


# Read All
def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transaction).offset(skip).limit(limit).all()


# Read One by ID
def get_transaction_by_id(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


# Update
def update_transaction(
    db: Session,
    transaction_id: int,
    crypto_name: str = None,
    amount: float = None,
    price_usd: float = None,
):
    db_transaction = (
        db.query(Transaction).filter(Transaction.id == transaction_id).first()
    )
    if not db_transaction:
        return None

    # Update fields if values are provided
    if crypto_name is not None:
        db_transaction.crypto_name = crypto_name
    if amount is not None:
        db_transaction.amount = amount
    if price_usd is not None:
        db_transaction.price_usd = price_usd

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


# Delete
def delete_transaction(db: Session, transaction_id: int):
    db_transaction = (
        db.query(Transaction).filter(Transaction.id == transaction_id).first()
    )
    if not db_transaction:
        return None

    db.delete(db_transaction)
    db.commit()
    return db_transaction
