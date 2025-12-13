from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import models, schemas, security
from database import get_db
import datetime # Import datetime

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
    )
    db.add(nueva_cuenta)
    db.commit()
    db.refresh(nueva_cuenta)

    if cuenta.saldo_inicial != 0:
        # Find or create a category for initial balance adjustments
        categoria_ajuste = db.query(models.Categoria).filter(
            models.Categoria.usuario_id == current_user.usuario_id
        ).first() # Check if any category exists
        
        if not categoria_ajuste:
            categoria_ajuste = models.Categoria(
                usuario_id=current_user.usuario_id,
                nombre_categoria="Ajustes de Saldo",
                tipo="Ingreso"
            )
            db.add(categoria_ajuste)
            db.flush()

        nuevo_movimiento = models.Movimiento(
            usuario_id=current_user.usuario_id,
            cuenta_id=nueva_cuenta.cuenta_id,
            categoria_id=categoria_ajuste.categoria_id,
            tipo="Ingreso",
            monto=abs(cuenta.saldo_inicial),
            descripcion="Saldo Inicial",
            fecha=datetime.datetime.now()
        )
        db.add(nuevo_movimiento)
        db.commit()
        db.refresh(nuevo_movimiento)

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
