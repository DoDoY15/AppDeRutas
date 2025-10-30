# AppDeRutas - Sistema de Optimización de Rutas

## 📋 Descripción
AppDeRutas es una aplicación de optimización de rutas que ayuda a gestionar y optimizar rutas de entrega y visitas comerciales.

## 🚀 Instalación

### Requisitos Previos
- Python 3.8+
- Node.js 14+
- npm
- Base de datos SQLite

### Backend (FastAPI)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload
```
### Frontend (React/TypeScript)
```bash
# Instalar dependencias
cd frontend
npm install

# Iniciar servidor de desarrollo
npm start
```
## 📚 API Documentation

La documentación de la API está disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 Licencia