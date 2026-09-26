from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.device_model import Device

def listar_devices(db: Session, device_type=None, is_available=None, brand=None, search=None):
    q = db.query(Device)
    if device_type: q = q.filter(Device.device_type == device_type)
    if is_available is not None: q = q.filter(Device.is_available == is_available)
    if brand: q = q.filter(Device.brand == brand)
    if search:
        term = f"%{search}%"
        q = q.filter(or_(Device.name.ilike(term), Device.serial_number.ilike(term)))
    return q.order_by(Device.id).all()

def buscar_device(db, device_id): return db.query(Device).filter(Device.id == device_id).first()
def buscar_por_serial(db, serial): return db.query(Device).filter(Device.serial_number == serial).first()

def crear_device(db, data):
    obj=Device(**data); db.add(obj); db.commit(); db.refresh(obj); return obj

def actualizar_device(db, obj, data):
    for k,v in data.items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

def eliminar_device(db,obj):
    db.delete(obj); db.commit()
