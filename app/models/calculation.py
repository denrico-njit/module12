import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.user import Base
from app.enums import OperationType


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    operand1 = Column(Float, nullable=False)
    operand2 = Column(Float, nullable=False)
    operation = Column(Enum(OperationType), nullable=False)
    result = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Calculation(id={self.id}, user_id={self.user_id}, operation={self.operation}, result={self.result})>"

    @classmethod
    def create(cls, db, user_id: UUID, type: OperationType, a: float, b: float) -> "Calculation":
        """Factory method to create and store a new calculation."""
        from app.operations import add, subtract, multiply, divide

        operations = {
            OperationType.add: add,
            OperationType.subtract: subtract,
            OperationType.multiply: multiply,
            OperationType.divide: divide,   
        }

        result = operations[type](a, b)
        calculation = cls(user_id=user_id, operand1=a, operand2=b, operation=type, result=result)
        db.add(calculation)
        db.flush()
        return calculation
