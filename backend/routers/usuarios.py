from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import schemas, models, security
from pydantic import BaseModel

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

class UserUpdate(BaseModel):
    nombre: str
    email: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

@router.get("/me", response_model=schemas.Usuario)
def read_users_me(current_user: models.Usuario = Depends(security.get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.Usuario)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    # Check if email is taken by another user
    existing_user = db.query(models.Usuario).filter(models.Usuario.email == user_update.email).first()
    if existing_user and existing_user.usuario_id != current_user.usuario_id:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    current_user.nombre = user_update.nombre
    current_user.email = user_update.email
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/cambiar-password")
def change_password(
    pass_update: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    if not security.verify_password(pass_update.current_password, current_user.contraseña):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    current_user.contraseña = security.get_password_hash(pass_update.new_password)
    db.commit()
    return {"message": "Contraseña actualizada correctamente"}
