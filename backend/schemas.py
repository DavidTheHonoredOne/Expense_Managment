from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- SEGURIDAD (JWT) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- USUARIO ---
class UsuarioBase(BaseModel):
    nombre: Optional[str] = None
    email: str 

class UsuarioCreate(UsuarioBase):
    contraseña: str

class Usuario(UsuarioBase):
    usuario_id: int
    fecha_registro: datetime
    estado: bool
    class Config:
        from_attributes = True

# --- CUENTA ---
class CuentaBase(BaseModel):
    nombre_cuenta: str
    tipo: Optional[str] = None
    saldo_actual: Decimal = 0

class CuentaCreate(CuentaBase):
    saldo_inicial: Decimal = 0 

class Cuenta(CuentaBase):
    cuenta_id: int
    usuario_id: int
    class Config:
        from_attributes = True

# --- CATEGORIA ---
class CategoriaBase(BaseModel):
    nombre_categoria: str
    tipo: str  

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    categoria_id: int
    usuario_id: int
    class Config:
        from_attributes = True

# --- MOVIMIENTO ---
class MovimientoBase(BaseModel):
    tipo: str 
    monto: Decimal
    descripcion: Optional[str] = None
    fecha: Optional[datetime] = None

class MovimientoCreate(MovimientoBase):
    cuenta_id: int
    categoria_id: int

class Movimiento(MovimientoBase):
    movimiento_id: int
    usuario_id: int
    cuenta_id: int
    categoria_id: int
    nombre_categoria: Optional[str] = None 
    nombre_cuenta: Optional[str] = None
    # New: Relationship to MovimientoMeta
    movimientos_meta: List["MovimientoMeta"] = [] # New: To support relationships

    class Config:
        from_attributes = True

# --- META ---
class MetaBase(BaseModel):
    nombre_meta: str
    monto_objetivo: Decimal
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None

class MetaCreate(MetaBase):
    pass

class Meta(MetaBase):
    meta_id: int
    usuario_id: int
    monto_actual: Decimal
    estado: bool
    progreso: Optional[float] = 0 
    movimientos_meta: List["MovimientoMeta"] = [] # New: To support relationships

    class Config:
        from_attributes = True

# --- MOVIMIENTO META (Pivote) ---
class MovimientoMetaBase(BaseModel):
    monto_destinado: Decimal
    fecha_asignacion: Optional[datetime] = None

class MovimientoMetaCreate(MovimientoMetaBase):
    meta_id: int
    movimiento_id: int

class MovimientoMeta(MovimientoMetaBase):
    movimiento_meta_id: int
    meta_id: int
    movimiento_id: int

    class Config:
        from_attributes = True

class MetaAbono(BaseModel):
    monto: Decimal
    cuenta_id: int # Nuevo campo requerido para abonar

# --- DASHBOARD ---
class DashboardResumen(BaseModel):
    total_ingresos: Decimal
    total_gastos: Decimal
    saldo_total: Decimal

# Update forward refs
Movimiento.model_rebuild()
Meta.model_rebuild()
