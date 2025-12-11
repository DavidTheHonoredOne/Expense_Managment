from typing import List
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import schemas, models, security

router = APIRouter(prefix="/metas", tags=["metas"])

@router.post("", response_model=schemas.Meta)
def crear_meta(
    meta: schemas.MetaCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    try:
        fecha_inicio_real = meta.fecha_inicio or datetime.datetime.now()
        fecha_fin_real = meta.fecha_fin
        if not fecha_fin_real:
            fecha_fin_real = fecha_inicio_real + datetime.timedelta(days=365) # Default to 1 year

        nueva_meta = models.Meta(
            usuario_id=current_user.usuario_id,
            nombre_meta=meta.nombre_meta,
            monto_objetivo=meta.monto_objetivo,
            monto_actual=0,
            fecha_inicio=fecha_inicio_real,
            fecha_fin=fecha_fin_real,
            estado=True
        )
        db.add(nueva_meta)
        db.commit()
        db.refresh(nueva_meta)
        return nueva_meta
    except Exception as e:
        print(f"Error al crear meta: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al crear meta: {e}")

@router.get("") 
def obtener_metas(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    return db.query(models.Meta).filter(models.Meta.usuario_id == current_user.usuario_id).all()

@router.post("/{meta_id}/abonar")
def abonar_meta(
    meta_id: int, 
    abono: schemas.MetaAbono,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    meta = db.query(models.Meta).filter(models.Meta.meta_id == meta_id, models.Meta.usuario_id == current_user.usuario_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    
    cuenta = db.query(models.Cuenta).filter(models.Cuenta.cuenta_id == abono.cuenta_id, models.Cuenta.usuario_id == current_user.usuario_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta de origen no encontrada o no pertenece al usuario")

    if cuenta.saldo_actual < abono.monto:
        raise HTTPException(status_code=400, detail="Saldo insuficiente en la cuenta de origen")

    if abono.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto a abonar debe ser mayor que cero")

    # Buscar una categoría por defecto para abonos a metas.
    categoria_abono = db.query(models.Categoria).filter(
        models.Categoria.usuario_id == current_user.usuario_id,
        func.lower(models.Categoria.nombre_categoria) == "ahorro"
    ).first()

    if not categoria_abono:
        categoria_abono = db.query(models.Categoria).filter(
            models.Categoria.usuario_id == current_user.usuario_id,
            func.lower(models.Categoria.nombre_categoria).in_(["general", "otros"])
        ).first()

    if not categoria_abono:
        categoria_abono = db.query(models.Categoria).filter(
            models.Categoria.usuario_id == current_user.usuario_id,
            func.lower(models.Categoria.tipo) == "ingreso"
        ).first()

    if not categoria_abono:
        raise HTTPException(status_code=400, detail="No se encontró una categoría adecuada para el abono a meta.")

    # Crear el movimiento de gasto desde la cuenta de origen
    new_movimiento = models.Movimiento(
        usuario_id=current_user.usuario_id,
        cuenta_id=abono.cuenta_id,
        categoria_id=categoria_abono.categoria_id,
        tipo="Gasto", # Se considera un gasto para la cuenta de origen
        monto=abono.monto,
        fecha=datetime.datetime.now(),
        descripcion=f"Abono a meta: {meta.nombre_meta}"
    )
    db.add(new_movimiento)
    
    # Actualizar saldos y meta
    cuenta.saldo_actual -= abono.monto
    meta.monto_actual += abono.monto
    
    if meta.monto_objetivo > 0:
        meta.progreso = float(meta.monto_actual) / float(meta.monto_objetivo)
    else:
        meta.progreso = 0

    # Crear el registro en MovimientoMeta
    db.flush() # Flush to get the ID of new_movimiento
    new_movimiento_meta = models.MovimientoMeta(
        meta_id=meta.meta_id,
        movimiento_id=new_movimiento.movimiento_id,
        monto_destinado=abono.monto,
        fecha_asignacion=datetime.datetime.now()
    )
    db.add(new_movimiento_meta)

    db.commit()
    db.refresh(meta)
    db.refresh(cuenta)
    db.refresh(new_movimiento)
    db.refresh(new_movimiento_meta)
    
    return {"message": "Abono exitoso", "nuevo_monto_meta": meta.monto_actual, "nuevo_saldo_cuenta": cuenta.saldo_actual}

@router.put("/{meta_id}", response_model=schemas.Meta)
def update_meta(
    meta_id: int,
    meta_update: schemas.MetaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    meta = db.query(models.Meta).filter(models.Meta.meta_id == meta_id, models.Meta.usuario_id == current_user.usuario_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta no encontrada")

    meta.nombre_meta = meta_update.nombre_meta
    meta.monto_objetivo = meta_update.monto_objetivo
    meta.fecha_fin = meta_update.fecha_fin
    
    db.commit()
    db.refresh(meta)
    return meta

@router.delete("/{meta_id}")
def delete_meta(
    meta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    meta = db.query(models.Meta).filter(models.Meta.meta_id == meta_id, models.Meta.usuario_id == current_user.usuario_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta no encontrada")

    # Opcional: Revertir los movimientos asociados a la meta si es necesario.
    # Por ahora, solo borramos la meta y los registros de movimiento_meta (si la DB tiene cascada)
    # Si no hay cascada, borrarlos manualmente
    db.query(models.MovimientoMeta).filter(models.MovimientoMeta.meta_id == meta_id).delete()
    
    db.delete(meta)
    db.commit()
    return {"message": "Meta eliminada"}
