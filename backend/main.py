from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os

import models, schemas, security
from database import engine, get_db

# Importamos los routers (Ahora sí existen todos)
from routers import categoria, metas, cuentas, movimientos, dashboard, usuarios

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Management API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://expense-managment-22pm.onrender.com",
]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectamos los routers (Esto habilita las rutas en /docs)
app.include_router(categoria.router)
app.include_router(metas.router)
app.include_router(cuentas.router)
app.include_router(movimientos.router)
app.include_router(dashboard.router)
app.include_router(usuarios.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Expense Management API"}

# --- TUS ENDPOINTS DE SEGURIDAD (Esto sí es tu responsabilidad) ---

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.contraseña):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user.email, "id": user.usuario_id}, 
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/usuarios/", response_model=schemas.Usuario)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    new_user = models.Usuario(
        nombre=user.nombre, 
        email=user.email, 
        contraseña=security.get_password_hash(user.contraseña),
        estado=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
