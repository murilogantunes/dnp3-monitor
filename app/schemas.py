from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceCreate(BaseModel):
    name: str
    host: str
    port: int = 20000
    dnp3_address: int
    active: bool = True
    analog_input_count: int = 10
    binary_input_count: int = 8
    double_point_count: int = 4

class DeviceResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    dnp3_address: int
    active: bool
    analog_input_count: int
    binary_input_count: int
    double_point_count: int

    class Config:
        from_attributes = True

class DevicePointCreate(BaseModel):
    point_index: int
    point_type: str
    point_name: str
    engineering_unit: str = ""
    description: str = ""

class DevicePointResponse(BaseModel):
    id: int
    device_id: int
    point_index: int
    point_type: str
    point_name: str
    engineering_unit: str
    description: str

    class Config:
        from_attributes = True

class MeasurementResponse(BaseModel):
    id: int
    device_id: int
    point_index: int
    point_type: str
    value: float
    timestamp: str

    class Config:
        from_attributes = True