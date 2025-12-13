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
    # 1. Validación de Datos
    meta = db.query(models.Meta).filter(models.Meta.meta_id == meta_id, models.Meta.usuario_id == current_user.usuario_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    
    cuenta = db.query(models.Cuenta).filter(models.Cuenta.cuenta_id == abono.cuenta_id, models.Cuenta.usuario_id == current_user.usuario_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta de origen no encontrada")

    monto_real = abs(abono.monto)
    if monto_real <= 0:
         raise HTTPException(status_code=400, detail="El monto debe ser mayor a cero")

    if cuenta.saldo_actual < monto_real:
        raise HTTPException(status_code=400, detail="Saldo insuficiente en la cuenta de origen")

    # 2. Gestión Automática de Categoría
    # Busca si existe una categoría llamada: "Meta: {meta.nombre_meta}"
    nombre_categoria = f"Meta: {meta.nombre_meta}"
    categoria = db.query(models.Categoria).filter(
        models.Categoria.usuario_id == current_user.usuario_id,
        models.Categoria.nombre_categoria == nombre_categoria
    ).first()

    if not categoria:
        # Si NO existe: Créala automáticamente
        categoria = models.Categoria(
            usuario_id=current_user.usuario_id,
            nombre_categoria=nombre_categoria,
            tipo='Gasto'
        )
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
    
    categoria_id_usar = categoria.categoria_id

    try:
        # 3. Transacción Atómica
        # Crea el Movimiento
        nuevo_movimiento = models.Movimiento(
            usuario_id=current_user.usuario_id,
            cuenta_id=cuenta.cuenta_id,
            categoria_id=categoria_id_usar,
            tipo="Gasto",
            monto=monto_real,
            descripcion=f"Abono a meta: {meta.nombre_meta}",
            fecha=datetime.datetime.now()
        )
        db.add(nuevo_movimiento)
        
        # Actualiza saldos
        cuenta.saldo_actual -= monto_real
        meta.monto_actual += monto_real
        
        db.flush() 
        
        # Crea la relación en Movimiento_Meta
        new_movimiento_meta = models.MovimientoMeta(
            meta_id=meta.meta_id,
            movimiento_id=nuevo_movimiento.movimiento_id,
            monto_destinado=monto_real,
            fecha_asignacion=datetime.datetime.now()
        )
        db.add(new_movimiento_meta)

        db.commit()
        db.refresh(meta)
        
        return {"message": "Abono exitoso", "meta": meta}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al abonar: {str(e)}")

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

    db.query(models.MovimientoMeta).filter(models.MovimientoMeta.meta_id == meta_id).delete()
    
    db.delete(meta)
    db.commit()
    return {"message": "Meta eliminada"}
