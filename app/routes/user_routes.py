from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

class User(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool

# Endpoint POST para crear usuario
@router.post("/")
def create_user(user: User):
    return {"message": "Usuario creado correctamente", "user": user}
