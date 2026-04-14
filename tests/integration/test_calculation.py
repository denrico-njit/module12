import pytest
from app.models.calculation import Calculation
from app.enums import OperationType


def test_create_addition(db_session, test_user):
    # Addition result should be stored correctly and linked to the user
    calc = Calculation.create(db_session, test_user.id, OperationType.add, 2, 3)
    db_session.commit()
    db_session.refresh(calc)
    assert calc.result == 5
    assert calc.operation == OperationType.add
    assert calc.user_id == test_user.id
    assert calc.id is not None
    assert calc.timestamp is not None


def test_create_subtraction(db_session, test_user):
    # Subtraction result should be persisted correctly
    calc = Calculation.create(db_session, test_user.id, OperationType.subtract, 10, 4)
    db_session.commit()
    db_session.refresh(calc)
    assert calc.result == 6


def test_create_multiplication(db_session, test_user):
    # Multiplication result should be persisted correctly
    calc = Calculation.create(db_session, test_user.id, OperationType.multiply, 3, 4)
    db_session.commit()
    db_session.refresh(calc)
    assert calc.result == 12


def test_create_division(db_session, test_user):
    # Division result should be stored as a float
    calc = Calculation.create(db_session, test_user.id, OperationType.divide, 10, 2)
    db_session.commit()
    db_session.refresh(calc)
    assert calc.result == 5.0


def test_divide_by_zero_raises(db_session, test_user):
    # Division by zero should raise ValueError at the model level
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        Calculation.create(db_session, test_user.id, OperationType.divide, 1, 0)


def test_calculation_persisted(db_session, test_user):
    # A committed calculation should be retrievable from the database by id
    calc = Calculation.create(db_session, test_user.id, OperationType.add, 1, 1)
    db_session.commit()
    fetched = db_session.query(Calculation).filter_by(id=calc.id).first()
    assert fetched is not None
    assert fetched.result == 2
