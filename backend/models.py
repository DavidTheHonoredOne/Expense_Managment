from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "Usuario"

    usuario_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    email = Column(String(100), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
    estado = Column(Boolean, default=True)

    # Relaciones
    cuentas = relationship("Cuenta", back_populates="usuario")
    categorias = relationship("Categoria", back_populates="usuario")
    movimientos = relationship("Movimiento", back_populates="usuario")
    metas = relationship("Meta", back_populates="usuario") # Updated: Refers to new Meta class

class Cuenta(Base):
    __tablename__ = "Cuenta"

    cuenta_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id"), nullable=False)
    nombre_cuenta = Column(String(100), nullable=False)
    saldo_actual = Column(DECIMAL(15, 2), default=0)

    # Relaciones
    usuario = relationship("Usuario", back_populates="cuentas")
    movimientos = relationship("Movimiento", back_populates="cuenta")

class Categoria(Base):
    __tablename__ = "Categoria"

    categoria_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id"), nullable=False)
    nombre_categoria = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False) # 'Ingreso' o 'Gasto'

    # Relaciones
    usuario = relationship("Usuario", back_populates="categorias")
    movimientos = relationship("Movimiento", back_populates="categoria")

class Meta(Base): # Renamed from MetaAhorro to Meta
    __tablename__ = "Meta"

    meta_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id"), nullable=False)
    nombre_meta = Column(String(100), nullable=False)
    monto_objetivo = Column(DECIMAL(15, 2), nullable=False)
    monto_actual = Column(DECIMAL(15, 2), default=0) # Ensure it's DECIMAL
    fecha_inicio = Column(DateTime, server_default=func.now(), nullable=False) # Added server_default
    fecha_fin = Column(DateTime, nullable=False)
    estado = Column(Boolean, default=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="metas")
    movimientos_meta = relationship("MovimientoMeta", back_populates="meta") # New relationship

class MovimientoMeta(Base): # New Pivote Table
    __tablename__ = "Movimiento_Meta"

    movimiento_meta_id = Column(Integer, primary_key=True, index=True)
    meta_id = Column(Integer, ForeignKey("Meta.meta_id"), nullable=False)
    movimiento_id = Column(Integer, ForeignKey("Movimiento.movimiento_id"), nullable=False)
    monto_destinado = Column(DECIMAL(15, 2), nullable=False)
    fecha_asignacion = Column(DateTime, server_default=func.now())

    # Relaciones
    meta = relationship("Meta", back_populates="movimientos_meta")
    movimiento = relationship("Movimiento", back_populates="movimientos_meta")

class Movimiento(Base):
    __tablename__ = "Movimiento"

    movimiento_id = Column(Integer, primary_key=True, index=True)
    cuenta_id = Column(Integer, ForeignKey("Cuenta.cuenta_id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("Categoria.categoria_id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id"), nullable=False)
    tipo = Column(String(20), nullable=False) # 'Ingreso' o 'Gasto'
    monto = Column(DECIMAL(15, 2), nullable=False)
    fecha = Column(DateTime, server_default=func.now()) # Use server_default
    descripcion = Column(Text)

    # Relaciones
    usuario = relationship("Usuario", back_populates="movimientos")
    categoria = relationship("Categoria", back_populates="movimientos")
    cuenta = relationship("Cuenta", back_populates="movimientos")
    movimientos_meta = relationship("MovimientoMeta", back_populates="movimiento") # New relationship
