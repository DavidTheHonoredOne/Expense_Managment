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
    cuenta = db.query(models.Cuenta).filter(
        models.Cuenta.cuenta_id == movimiento.cuenta_id, 
        models.Cuenta.usuario_id == current_user.usuario_id
    ).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada o no pertenece al usuario")
    
    categoria = db.query(models.Categoria).filter(
        models.Categoria.categoria_id == movimiento.categoria_id, 
        models.Categoria.usuario_id == current_user.usuario_id
    ).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o no pertenece al usuario")
    
    mov_data = movimiento.model_dump(exclude={"usuario_id"})
    new_movimiento = models.Movimiento(
        **mov_data,
        usuario_id=current_user.usuario_id
    )
    db.add(new_movimiento)
    
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

    link_meta = db.query(models.MovimientoMeta).filter(models.MovimientoMeta.movimiento_id == movimiento_id).first()

    if link_meta and movimiento.tipo != existing_movimiento.tipo:
        raise HTTPException(status_code=400, detail="No se puede cambiar el tipo de un abono a meta")

    old_monto = existing_movimiento.monto
    old_cuenta = existing_movimiento.cuenta

    if existing_movimiento.tipo.lower() == 'ingreso':
        old_cuenta.saldo_actual -= old_monto
    else:
        old_cuenta.saldo_actual += old_monto

    for field, value in movimiento.model_dump(exclude_unset=True).items():
        setattr(existing_movimiento, field, value)
    
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
    
    if link_meta:
        meta = db.query(models.Meta).filter(models.Meta.meta_id == link_meta.meta_id).first()
        if meta:
            diferencia = existing_movimiento.monto - old_monto
            meta.monto_actual += diferencia

    db.commit()
    db.refresh(existing_movimiento)

    if existing_movimiento.categoria:
        existing_movimiento.nombre_categoria = existing_movimiento.categoria.nombre_categoria
    if existing_movimiento.cuenta:
        existing_movimiento.nombre_cuenta = existing_movimiento.cuenta.nombre_cuenta

    return existing_movimiento

@router.delete("/{movimiento_id}")
def delete_movimiento(movimiento_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    movimiento = db.query(models.Movimiento).filter(models.Movimiento.movimiento_id == movimiento_id, models.Movimiento.usuario_id == current_user.usuario_id).first()
    if not movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    link_meta = db.query(models.MovimientoMeta).filter(models.MovimientoMeta.movimiento_id == movimiento_id).first()

    if link_meta:
        meta = db.query(models.Meta).filter(models.Meta.meta_id == link_meta.meta_id).first()
        if meta:
            meta.monto_actual -= movimiento.monto
            if meta.monto_actual < 0:
                meta.monto_actual = 0
        db.delete(link_meta)

    cuenta = movimiento.cuenta
    if movimiento.tipo.lower() == 'ingreso':
        cuenta.saldo_actual -= movimiento.monto
    else:
        cuenta.saldo_actual += movimiento.monto

    db.delete(movimiento)
    db.commit()
    return {"message": "Movimiento eliminado exitosamente"}
