import pytest
from pydantic import ValidationError
from app.schemas.calculation import CalculationCreate
from app.enums import OperationType


def test_calculation_create_valid_add():
    # Valid add operation should be accepted without error
    calc = CalculationCreate(a=1, b=2, type=OperationType.add)
    assert calc.a == 1
    assert calc.b == 2
    assert calc.type == OperationType.add


def test_calculation_create_valid_subtract():
    # Valid subtract operation should be accepted without error
    calc = CalculationCreate(a=5, b=3, type=OperationType.subtract)
    assert calc.result if hasattr(calc, 'result') else calc.a - calc.b == 2


def test_calculation_create_valid_multiply():
    # Valid multiply operation should be accepted without error
    calc = CalculationCreate(a=3, b=4, type=OperationType.multiply)
    assert calc.a == 3
    assert calc.b == 4
    assert calc.type == OperationType.multiply


def test_calculation_create_valid_divide():
    # Valid divide operation with non-zero divisor should be accepted
    calc = CalculationCreate(a=10, b=2, type=OperationType.divide)
    assert calc.a == 10
    assert calc.b == 2
    assert calc.type == OperationType.divide


def test_calculation_create_zero_divisor():
    # Dividing by zero should raise a ValidationError
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationCreate(a=1, b=0, type=OperationType.divide)


def test_calculation_create_invalid_type():
    # An unrecognized operation type string should raise a ValidationError
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, b=2, type="invalid")


def test_calculation_create_missing_fields():
    # Missing required fields should raise a ValidationError
    with pytest.raises(ValidationError):
        CalculationCreate(a=1)
