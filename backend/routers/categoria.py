from typing import List
from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
import schemas
import models
import security

router = APIRouter(prefix="/categorias", tags=["categorias"])

# Endpoint para crear una categoria
@router.post("/", response_model=schemas.Categoria)
def crear_categoria(
    categoria: schemas.CategoriaCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    nueva_categoria = models.Categoria(
        usuario_id=current_user.usuario_id,
        nombre_categoria=categoria.nombre_categoria,
        tipo=categoria.tipo
    )
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

# Endpoint para obtener todas las categorias
@router.get("/", response_model=List[schemas.Categoria])
def obtener_categorias(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    return db.query(models.Categoria).filter(models.Categoria.usuario_id == current_user.usuario_id).all()

# Endpoint para eliminar una categoria
@router.delete("/{categoria_id}")
def eliminar_categoria(
    categoria_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    categoria = db.query(models.Categoria).filter(
        models.Categoria.categoria_id == categoria_id, 
        models.Categoria.usuario_id == current_user.usuario_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
    # Check dependencies (FK constraint)
    # models.Categoria doesn't have explicit relationship check here but let's assume if it has movements we block or DB throws error
    # Better to check
    if categoria.movimientos:
        raise HTTPException(status_code=400, detail="No se puede eliminar una categoría con movimientos asociados")
        
    db.delete(categoria)
    db.commit()
    return {"message": "Categoría eliminada"}
