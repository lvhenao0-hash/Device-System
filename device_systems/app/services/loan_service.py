from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from app.models.loan_model import Loan
from app.models.user_model import User
from app.models.device_model import Device

def listar_loans(db: Session, status=None, user_email=None, device_type=None, user_id=None, device_id=None):
    q = db.query(Loan).join(User, Loan.user_id == User.id).join(Device, Loan.device_id == Device.id)
    conditions = []
    if status: conditions.append(Loan.status == status)
    if user_email: conditions.append(User.email.ilike(f"%{user_email}%"))
    if device_type: conditions.append(Device.device_type == device_type)
    if user_id: conditions.append(Loan.user_id == user_id)
    if device_id: conditions.append(Loan.device_id == device_id)
    if conditions: q = q.filter(and_(*conditions))
    return q.options(joinedload(Loan.user), joinedload(Loan.device)).order_by(Loan.id.desc()).all()

def buscar_loan(db, loan_id):
    return db.query(Loan).options(joinedload(Loan.user), joinedload(Loan.device)).filter(Loan.id == loan_id).first()

def crear_loan(db, user, device):
    loan=Loan(user_id=user.id, device_id=device.id, status="active")
    device.is_available=False
    db.add(loan); db.commit(); db.refresh(loan); return buscar_loan(db, loan.id)

def devolver_loan(db, loan):
    loan.status="returned"; loan.return_date=datetime.utcnow(); loan.device.is_available=True
    db.commit(); db.refresh(loan); return loan
