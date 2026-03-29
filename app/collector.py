import time
import random
import threading
import multiprocessing
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def simulate_analog_value(point_index: int) -> float:
    base_values = {
        0: (13.0, 15.0),
        1: (0.0, 100.0),
        2: (0.0, 50.0),
    }
    min_val, max_val = base_values.get(point_index, (0.0, 100.0))
    return round(random.uniform(min_val, max_val), 3)

def simulate_binary_value() -> float:
    return float(random.choice([0, 1]))

def simulate_double_point_value() -> float:
    return float(random.choice([0, 1, 2, 3]))

def collect_device(device: models.Device, db: Session):
    try:
        for i in range(device.analog_input_count):
            measurement = models.Measurement(
                device_id=device.id,
                point_index=i,
                point_type="analog_input",
                value=simulate_analog_value(i),
                timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )
            db.add(measurement)
        for i in range(device.binary_input_count):
            measurement = models.Measurement(
                device_id=device.id,
                point_index=i,
                point_type="binary_input",
                value=simulate_binary_value(),
                timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )
            db.add(measurement)
        for i in range(device.double_point_count):
            measurement = models.Measurement(
                device_id=device.id,
                point_index=i,
                point_type="double_point",
                value=simulate_double_point_value(),
                timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )
            db.add(measurement)
        db.commit()
        print(f"[{datetime.utcnow()}] Collected data from device: {device.name}", flush=True)
    except Exception as e:
        print(f"[{datetime.utcnow()}] Error collecting from {device.name}: {e}", flush=True)
        db.rollback()

def collect_once():
    db = SessionLocal()
    try:
        devices = db.query(models.Device).filter(
            models.Device.active == True
        ).all()
        print(f"[{datetime.utcnow()}] Scanning {len(devices)} active devices...", flush=True)
        for device in devices:
            collect_device(device, db)
    finally:
        db.close()

def _collector_process():
    print("Collector process started...", flush=True)
    while True:
        try:
            collect_once()
        except Exception as e:
            print(f"[{datetime.utcnow()}] Error in collector: {e}", flush=True)
        time.sleep(10)

def start_collector():
    process = multiprocessing.Process(target=_collector_process, daemon=True)
    process.start()
    print(f"Collector process started with PID: {process.pid}", flush=True)
    return process
