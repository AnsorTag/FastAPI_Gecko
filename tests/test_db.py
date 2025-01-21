# test_db.py
import pytest
from sqlalchemy.orm import Session
from app.databases.db import Base, engine, SessionLocal
from app.models.model import Transaction
from app.crud import (
    create_transaction,
    get_transactions,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
)


# Fixture to create a new database session for each test
@pytest.fixture(scope="function")
def db_session():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a new session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)


# Test create_transaction
def test_create_transaction(db_session: Session):
    transaction = create_transaction(db_session, "bitcoin", 1.0, 50000.0)
    assert transaction.id is not None
    assert transaction.crypto_name == "bitcoin"
    assert transaction.amount == 1.0
    assert transaction.price_usd == 50000.0


# Test get_transactions
def test_get_transactions(db_session: Session):
    create_transaction(db_session, "bitcoin", 1.0, 50000.0)
    create_transaction(db_session, "ethereum", 2.0, 3000.0)

    transactions = get_transactions(db_session)
    assert len(transactions) == 2
    assert transactions[0].crypto_name == "bitcoin"
    assert transactions[1].crypto_name == "ethereum"


# Test get_transaction_by_id
def test_get_transaction_by_id(db_session: Session):
    transaction = create_transaction(db_session, "bitcoin", 1.0, 50000.0)
    fetched_transaction = get_transaction_by_id(db_session, transaction.id)
    assert fetched_transaction is not None
    assert fetched_transaction.crypto_name == "bitcoin"


# Test update_transaction
def test_update_transaction(db_session: Session):
    transaction = create_transaction(db_session, "bitcoin", 1.0, 50000.0)
    updated_transaction = update_transaction(
        db_session, transaction.id, crypto_name="ethereum"
    )
    assert updated_transaction is not None
    assert updated_transaction.crypto_name == "ethereum"


# Test delete_transaction
def test_delete_transaction(db_session: Session):
    transaction = create_transaction(db_session, "bitcoin", 1.0, 50000.0)
    deleted_transaction = delete_transaction(db_session, transaction.id)
    assert deleted_transaction is not None
    assert get_transaction_by_id(db_session, transaction.id) is None
