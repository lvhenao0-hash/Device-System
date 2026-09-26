from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.dependencies.database_dependency import get_db
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceResponse, DeviceUpdate
from app.services import device_service

router = APIRouter(prefix="/devices", tags=["Devices"])

@router.get("", response_model=List[DeviceResponse], summary="Listar dispositivos")
def listar_devices(
    device_type: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    brand: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return device_service.listar_devices(db, device_type, is_available, brand, search)

@router.get("/{device_id}", response_model=DeviceResponse, summary="Consultar dispositivo")
def obtener_device(device_id: int, db: Session = Depends(get_db)):
    device = device_service.buscar_device(db, device_id)
    if not device:
        raise HTTPException(404, "Dispositivo no encontrado")
    return device

@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, summary="Crear dispositivo")
def crear_device(datos: DeviceCreate, db: Session = Depends(get_db)):
    if device_service.buscar_por_serial(db, datos.serial_number):
        raise HTTPException(400, "El número de serie ya existe")
    return device_service.crear_device(db, datos.model_dump())

@router.put("/{device_id}", response_model=DeviceResponse, summary="Actualizar dispositivo")
def actualizar_device(device_id: int, datos: DeviceUpdate, db: Session = Depends(get_db)):
    device = device_service.buscar_device(db, device_id)
    if not device: raise HTTPException(404, "Dispositivo no encontrado")
    other = device_service.buscar_por_serial(db, datos.serial_number)
    if other and other.id != device.id: raise HTTPException(400, "El número de serie ya existe")
    return device_service.actualizar_device(db, device, datos.model_dump())

@router.patch("/{device_id}", response_model=DeviceResponse, summary="Actualizar parcialmente dispositivo")
def patch_device(device_id: int, datos: DevicePatch, db: Session = Depends(get_db)):
    device = device_service.buscar_device(db, device_id)
    if not device: raise HTTPException(404, "Dispositivo no encontrado")
    data = datos.model_dump(exclude_unset=True)
    if not data: raise HTTPException(400, "Debes enviar al menos un campo")
    if "serial_number" in data:
        other = device_service.buscar_por_serial(db, data["serial_number"])
        if other and other.id != device.id: raise HTTPException(400, "El número de serie ya existe")
    return device_service.actualizar_device(db, device, data)

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar dispositivo")
def eliminar_device(device_id: int, db: Session = Depends(get_db)):
    device = device_service.buscar_device(db, device_id)
    if not device: raise HTTPException(404, "Dispositivo no encontrado")
    if device.loans: raise HTTPException(409, "No se puede eliminar un dispositivo con historial de préstamos")
    device_service.eliminar_device(db, device)
    return None


@router.get("/{device_id}/loans", summary="Consultar historial de préstamos del dispositivo")
def historial_device(device_id: int, db: Session = Depends(get_db)):
    from app.services.loan_service import listar_loans
    if device_service.buscar_device(db, device_id) is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return listar_loans(db, device_id=device_id)
