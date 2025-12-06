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
    
    # CORRECCIÓN: Esta línea ahora sí encontrará la clase 'MetaAhorro' de abajo
    metas = relationship("MetaAhorro", back_populates="usuario")


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


# CORRECCIÓN: Renombrada de 'Meta' a 'MetaAhorro' para evitar el error
class MetaAhorro(Base):
    __tablename__ = "Meta_Ahorro"

    meta_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id"), nullable=False)
    nombre_meta = Column(String(100), nullable=False)
    monto_objetivo = Column(DECIMAL(15, 2), nullable=False)
    monto_actual = Column(DECIMAL(15, 2), default=0)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    estado = Column(Boolean, default=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="metas")
    
    # NOTA: He comentado esto temporalmente porque 'Movimiento' no tiene clave foránea a Meta todavía.
    # Si lo descomentas ahora, te dará error 500.
    # movimientos = relationship("Movimiento", back_populates="meta")


class Movimiento(Base):
    __tablename__ = "Movimiento"

    movimiento_id = Column(Integer, primary_key=True, index=True)
    cuenta_id = Column(Integer, ForeignKey("Cuenta.cuenta_id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("Categoria.categoria_id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id"), nullable=False)
    tipo = Column(String(20), nullable=False) # 'Ingreso' o 'Gasto'
    monto = Column(DECIMAL(15, 2), nullable=False)
    fecha = Column(DateTime, server_default=func.now())
    descripcion = Column(Text)

    # Relaciones
    usuario = relationship("Usuario", back_populates="movimientos")
    categoria = relationship("Categoria", back_populates="movimientos")
    cuenta = relationship("Cuenta", back_populates="movimientos")