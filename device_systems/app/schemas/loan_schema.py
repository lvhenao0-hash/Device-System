from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict

LoanStatus = Literal["active", "returned", "overdue"]

class LoanCreate(BaseModel):
    user_id: int
    device_id: int

class LoanUpdate(BaseModel):
    status: Optional[LoanStatus] = None

class LoanUserResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class LoanDeviceResponse(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str
    model_config = ConfigDict(from_attributes=True)

class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime] = None
    status: str
    model_config = ConfigDict(from_attributes=True)

class LoanDetailResponse(BaseModel):
    loan_id: int
    status: str
    loan_date: datetime
    return_date: Optional[datetime] = None
    user: LoanUserResponse
    device: LoanDeviceResponse
