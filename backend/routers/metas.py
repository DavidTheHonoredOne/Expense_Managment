from typing import List
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas, models, security

router = APIRouter(prefix="/metas", tags=["metas"])

@router.post("/", response_model=schemas.MetaAhorro)
def crear_meta(
    meta: schemas.MetaAhorroCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    nueva_meta = models.MetaAhorro(
        usuario_id=current_user.usuario_id,
        nombre_meta=meta.nombre_meta,
        monto_objetivo=meta.monto_objetivo,
        monto_actual=0,
        fecha_inicio=meta.fecha_inicio or datetime.datetime.now(),
        fecha_fin=meta.fecha_fin,
        estado=True
    )
    db.add(nueva_meta)
    db.commit()
    db.refresh(nueva_meta)
    return nueva_meta

@router.get("/", response_model=List[schemas.MetaAhorro])
def obtener_metas(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    return db.query(models.MetaAhorro).filter(models.MetaAhorro.usuario_id == current_user.usuario_id).all()

# Endpoint para abonar (Requerido en api.js: /metas/{metaId}/abonar)
@router.post("/{meta_id}/abonar")
def abonar_meta(
    meta_id: int, 
    # Using a Pydantic model for body would be better but keeping it simple as per previous structure or assume user sends json
    # Let's use Body or a simple schema
    # The api.js sends { monto }
    # I'll create a local pydantic model or use dict
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    monto = payload.get("monto")
    if not monto:
         raise HTTPException(status_code=400, detail="Monto requerido")
         
    meta = db.query(models.MetaAhorro).filter(models.MetaAhorro.meta_id == meta_id, models.MetaAhorro.usuario_id == current_user.usuario_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    
    meta.monto_actual += float(monto)
    
    # Calculate progress? It's calculated in frontend or property?
    # Schema has progress: Optional[float].
    if meta.monto_objetivo > 0:
        meta.progreso = float(meta.monto_actual) / float(meta.monto_objetivo)
    else:
        meta.progreso = 0
        
    db.commit()
    return {"message": "Abono exitoso", "nuevo_monto": meta.monto_actual}
