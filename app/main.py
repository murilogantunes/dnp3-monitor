from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from collector import start_collector

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_collector()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "service": "dnp3-monitor"}

@app.get("/info")
def info():
    return {
        "project": "dnp3-monitor",
        "version": "0.1.0",
        "protocols": ["dnp3"]
    }

@app.post("/devices", response_model=schemas.DeviceResponse)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = models.Device(
        name=device.name,
        host=device.host,
        port=device.port,
        dnp3_address=device.dnp3_address,
        active=device.active,
        analog_input_count=device.analog_input_count,
        binary_input_count=device.binary_input_count,
        double_point_count=device.double_point_count
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.get("/devices", response_model=list[schemas.DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    return devices

@app.get("/devices/{device_id}", response_model=schemas.DeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.post("/devices/{device_id}/points", response_model=schemas.DevicePointResponse)
def create_point(device_id: int, point: schemas.DevicePointCreate, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    existing = db.query(models.DevicePoint).filter(
        models.DevicePoint.device_id == device_id,
        models.DevicePoint.point_index == point.point_index,
        models.DevicePoint.point_type == point.point_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Point already exists")
    db_point = models.DevicePoint(
        device_id=device_id,
        point_index=point.point_index,
        point_type=point.point_type,
        point_name=point.point_name,
        engineering_unit=point.engineering_unit,
        description=point.description
    )
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    return db_point

@app.get("/devices/{device_id}/points", response_model=list[schemas.DevicePointResponse])
def list_points(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    points = db.query(models.DevicePoint).filter(
        models.DevicePoint.device_id == device_id
    ).all()
    return points

@app.get("/devices/{device_id}/measurements", response_model=list[schemas.MeasurementResponse])
def get_measurements(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    measurements = db.query(models.Measurement).filter(
        models.Measurement.device_id == device_id
    ).all()
    return measurements

@app.get("/measurements", response_model=list[schemas.MeasurementResponse])
def get_all_measurements(db: Session = Depends(get_db)):
    measurements = db.query(models.Measurement).all()
    return measurements
