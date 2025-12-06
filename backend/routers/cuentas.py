from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, security
from database import get_db

router = APIRouter(prefix="/cuentas", tags=["cuentas"])

@router.get("/", response_model=List[schemas.Cuenta])
def obtener_cuentas(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    return db.query(models.Cuenta).filter(models.Cuenta.usuario_id == current_user.usuario_id).all()

@router.post("/", response_model=schemas.Cuenta)
def crear_cuenta(
    cuenta: schemas.CuentaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    nueva_cuenta = models.Cuenta(
        nombre_cuenta=cuenta.nombre_cuenta,
        usuario_id=current_user.usuario_id,
        saldo_actual=cuenta.saldo_inicial
        # tipo field is optional in schema but usually present. Let's check schema.
        # schemas.CuentaBase has tipo: Optional[str]
        # models.Cuenta does NOT seem to have 'tipo' column in the `models.py` I read earlier?
        # Let's check `models.py` content again from history.
    )
    # models.py for Cuenta:
    # cuenta_id, usuario_id, nombre_cuenta, saldo_actual.
    # NO 'tipo' column in models.py for Cuenta!
    # But schemas.py has 'tipo'.
    # I should strictly follow models.py or add the column.
    # Since I cannot easily migrate DB schema without Alembic (and I don't want to break things if I can't run migrations easily),
    # I will ignore 'tipo' if it's not in the model, OR I assumed it was there.
    # Let's check `models.py` content I read.
    # `class Cuenta(Base): ... nombre_cuenta, saldo_actual`. No `tipo`.
    # `class Categoria(Base): ... tipo`.
    
    # So for Cuenta, I won't save `tipo`.
    
    db.add(nueva_cuenta)
    db.commit()
    db.refresh(nueva_cuenta)
    return nueva_cuenta

@router.delete("/{cuenta_id}")
def eliminar_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    cuenta = db.query(models.Cuenta).filter(models.Cuenta.cuenta_id == cuenta_id, models.Cuenta.usuario_id == current_user.usuario_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    # Check for movements
    if cuenta.movimientos: # Relationship
         raise HTTPException(status_code=400, detail="No se puede eliminar una cuenta con movimientos asociados")

    db.delete(cuenta)
    db.commit()
    return {"message": "Cuenta eliminada"}
