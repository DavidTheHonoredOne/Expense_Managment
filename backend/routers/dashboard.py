from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import schemas, models, security
from database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/", response_model=schemas.DashboardResumen)
def obtener_resumen(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    # Calculate totals from DB
    
    # Total Ingresos
    ingresos = db.query(func.sum(models.Movimiento.monto)).filter(
        models.Movimiento.usuario_id == current_user.usuario_id,
        func.lower(models.Movimiento.tipo) == 'ingreso'
    ).scalar() or 0

    # Total Gastos
    gastos = db.query(func.sum(models.Movimiento.monto)).filter(
        models.Movimiento.usuario_id == current_user.usuario_id,
        func.lower(models.Movimiento.tipo) == 'gasto'
    ).scalar() or 0

    # Saldo Total (Sum of accounts)
    saldo_total = db.query(func.sum(models.Cuenta.saldo_actual)).filter(
        models.Cuenta.usuario_id == current_user.usuario_id
    ).scalar() or 0

    return {
        "total_ingresos": ingresos,
        "total_gastos": gastos,
        "saldo_total": saldo_total
    }
