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
