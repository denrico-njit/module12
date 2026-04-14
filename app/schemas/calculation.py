from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, model_validator, ConfigDict
from app.enums import OperationType


class CalculationCreate(BaseModel):
    a: float
    b: float
    type: OperationType

    @model_validator(mode="after")
    def check_no_zero_divisor(self):
        if self.type == OperationType.divide and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self


class CalculationRead(BaseModel):
    id: UUID
    user_id: UUID
    a: float
    b: float
    type: OperationType
    result: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)