from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, security
from database import get_db

router = APIRouter(prefix="/movimientos", tags=["movimientos"])

@router.get("/", response_model=List[schemas.Movimiento])
def get_movimientos(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    movimientos = db.query(models.Movimiento).filter(
        models.Movimiento.usuario_id == current_user.usuario_id
    ).order_by(models.Movimiento.fecha.desc()).all()
    
    # Populate optional fields
    for m in movimientos:
        if m.categoria:
            m.nombre_categoria = m.categoria.nombre_categoria
        if m.cuenta:
            m.nombre_cuenta = m.cuenta.nombre_cuenta
            
    return movimientos

@router.post("/", response_model=schemas.Movimiento)
def create_movimiento(
    movimiento: schemas.MovimientoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    # Verify account ownership
    cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.cuenta_id == movimiento.cuenta_id, 
        models.Cuenta.usuario_id == current_user.usuario_id
    ).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada o no pertenece al usuario")
    
    # Verify category ownership
    categoria = db.query(models.Categoria).filter(
        models.Categoria.categoria_id == movimiento.categoria_id, 
        models.Categoria.usuario_id == current_user.usuario_id
    ).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o no pertenece al usuario")
    
    # Create movement
    # We ignore usuario_id from the body if passed, and use current_user
    mov_data = movimiento.model_dump(exclude={"usuario_id"})
    new_movimiento = models.Movimiento(
        **mov_data,
        usuario_id=current_user.usuario_id
    )
    db.add(new_movimiento)
    
    # Update balance
    if new_movimiento.tipo.lower() == 'ingreso':
        cuenta.saldo_actual += new_movimiento.monto
    else:
        cuenta.saldo_actual -= new_movimiento.monto
        
    db.commit()
    db.refresh(new_movimiento)
    
    new_movimiento.nombre_categoria = categoria.nombre_categoria
    new_movimiento.nombre_cuenta = cuenta.nombre_cuenta
    
    return new_movimiento

@router.put("/{movimiento_id}", response_model=schemas.Movimiento)
def update_movimiento(
    movimiento_id: int,
    movimiento: schemas.MovimientoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    existing_movimiento = db.query(models.Movimiento).filter(
        models.Movimiento.movimiento_id == movimiento_id,
        models.Movimiento.usuario_id == current_user.usuario_id
    ).first()

    if not existing_movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    
    # Revert old balance first
    old_cuenta = existing_movimiento.cuenta
    if existing_movimiento.tipo.lower() == 'ingreso':
        old_cuenta.saldo_actual -= existing_movimiento.monto
    else:
        old_cuenta.saldo_actual += existing_movimiento.monto

    # Update movement fields
    for field, value in movimiento.model_dump(exclude_unset=True).items():
        setattr(existing_movimiento, field, value)
    
    # Apply new balance
    new_cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.cuenta_id == movimiento.cuenta_id, 
        models.Cuenta.usuario_id == current_user.usuario_id
    ).first()
    if not new_cuenta:
        raise HTTPException(status_code=404, detail="Nueva cuenta no encontrada o no pertenece al usuario")

    if existing_movimiento.tipo.lower() == 'ingreso':
        new_cuenta.saldo_actual += existing_movimiento.monto
    else:
        new_cuenta.saldo_actual -= existing_movimiento.monto

    db.commit()
    db.refresh(existing_movimiento)

    # Populate optional fields for response
    if existing_movimiento.categoria:
        existing_movimiento.nombre_categoria = existing_movimiento.categoria.nombre_categoria
    if existing_movimiento.cuenta:
        existing_movimiento.nombre_cuenta = existing_movimiento.cuenta.nombre_cuenta

    return existing_movimiento

@router.delete("/{movimiento_id}")
def delete_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    mov = db.query(models.Movimiento).filter(
        models.Movimiento.movimiento_id == movimiento_id, 
        models.Movimiento.usuario_id == current_user.usuario_id
    ).first()
    
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    
    # Revert balance
    cuenta = mov.cuenta
    if mov.tipo.lower() == 'ingreso':
        cuenta.saldo_actual -= mov.monto
    else:
        cuenta.saldo_actual += mov.monto
        
    db.delete(mov)
    db.commit()
    return {"message": "Movimiento eliminado"}
