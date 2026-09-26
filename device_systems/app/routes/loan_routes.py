from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies.database_dependency import get_db
from app.models.loan_model import Loan
from app.models.user_model import User
from app.models.device_model import Device
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["Loans"])

def detail(loan):
    return {"loan_id": loan.id, "status": loan.status, "loan_date": loan.loan_date,
            "return_date": loan.return_date, "user": loan.user, "device": loan.device}

@router.get("", response_model=List[LoanResponse], summary="Listar préstamos")
def listar_loans(status: Optional[str]=Query(None), user_email: Optional[str]=Query(None),
                 device_type: Optional[str]=Query(None), user_id: Optional[int]=Query(None),
                 device_id: Optional[int]=Query(None), db: Session=Depends(get_db)):
    if status and status not in {"active","returned","overdue"}:
        raise HTTPException(422, "Estado inválido")
    return loan_service.listar_loans(db,status,user_email,device_type,user_id,device_id)

@router.get("/details", response_model=List[LoanDetailResponse], summary="Consultar préstamos con joins")
def loan_details(status: Optional[str]=None, user_email: Optional[str]=None,
                 device_type: Optional[str]=None, db: Session=Depends(get_db)):
    return [detail(x) for x in loan_service.listar_loans(db,status,user_email,device_type)]

@router.get("/{loan_id}", response_model=LoanDetailResponse, summary="Consultar préstamo")
def get_loan(loan_id:int, db:Session=Depends(get_db)):
    loan=loan_service.buscar_loan(db,loan_id)
    if not loan: raise HTTPException(404,"Préstamo no encontrado")
    return detail(loan)

@router.post("", response_model=LoanDetailResponse, status_code=201, summary="Registrar préstamo")
def crear_loan(datos:LoanCreate, db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==datos.user_id).first()
    if not user: raise HTTPException(404,"Usuario no encontrado")
    device=db.query(Device).filter(Device.id==datos.device_id).first()
    if not device: raise HTTPException(404,"Dispositivo no encontrado")
    if not device.is_available: raise HTTPException(409,"El dispositivo no está disponible")
    return detail(loan_service.crear_loan(db,user,device))

@router.patch("/{loan_id}/return", response_model=LoanDetailResponse, summary="Devolver préstamo")
def return_loan(loan_id:int, db:Session=Depends(get_db)):
    loan=loan_service.buscar_loan(db,loan_id)
    if not loan: raise HTTPException(404,"Préstamo no encontrado")
    if loan.status=="returned": raise HTTPException(409,"El préstamo ya fue devuelto")
    return detail(loan_service.devolver_loan(db,loan))
