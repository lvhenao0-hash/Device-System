from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class DeviceBase(BaseModel):
    name: str = Field(..., min_length=2)
    serial_number: str = Field(..., min_length=2)
    device_type: str = Field(..., min_length=2)
    brand: Optional[str] = None
    is_available: bool = True

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    pass

class DevicePatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    serial_number: Optional[str] = Field(None, min_length=2)
    device_type: Optional[str] = Field(None, min_length=2)
    brand: Optional[str] = None
    is_available: Optional[bool] = None

class DeviceResponse(DeviceBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
