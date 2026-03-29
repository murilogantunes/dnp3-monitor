from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, default=20000)
    dnp3_address = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)
    analog_input_count = Column(Integer, default=10)
    binary_input_count = Column(Integer, default=8)
    double_point_count = Column(Integer, default=4)

    measurements = relationship("Measurement", back_populates="device")
    points = relationship("DevicePoint", back_populates="device")

class DevicePoint(Base):
    __tablename__ = "device_points"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    point_index = Column(Integer, nullable=False)
    point_type = Column(String, nullable=False)
    point_name = Column(String, nullable=False)
    engineering_unit = Column(String, default="")
    description = Column(String, default="")

    device = relationship("Device", back_populates="points")

class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    point_index = Column(Integer, nullable=False)
    point_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(String, default=lambda: datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    device = relationship("Device", back_populates="measurements")