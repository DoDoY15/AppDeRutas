# 🛣️ Aplicativo de Optimización de Rutas (VRP)

Este proyecto implementa una solución robusta para el Problema de Ruteo de Vehículos (VRP), que calcula la agenda semanal óptima para un equipo de vendedores, minimizando el tiempo de desplazamiento y respetando las restricciones de capacidad diaria (tiempo de trabajo y número máximo de visitas).

El sistema está construido en FastAPI (Python) para el backend y React/TypeScript para el frontend.

## 🎯 Objetivo del Sistema

El objetivo principal es transformar dos archivos de datos de entrada (`Usuarios` y `PDVs`) en una **agenda semanal optimizada**, garantizando que cada PDV reciba el número correcto de visitas por semana (Múltiples Pasadas) y que el tiempo de desplazamiento sea minimizado usando datos de tráfico en tiempo real (caché de Google Maps).

---

## ⚙️ 1. Entregables y Estructura

### 1.1. Estructura del Repositorio

```
/APP ROTAS
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core (configuracion y seguridad para possible escalabilidad)
│   │   ├── crud/ (Lógica de Upsert y Caché DB)
│   │   ├── db/ (Modelos SQLAlchemy)
│   │   ├──  services/ (Algoritmo y API JIT)
│   │   └── utils (para possible escalabilidad)
│   ├── main.py
│   └── .env (o config.py)
│
├── frontend/
│   └── src/ (Código React/TSX)
│
└── README.md
```

💻 2. Instrucciones de Instalación y Ejecución

Prerrequisitos

1.  **Python 3.9+** (o la versión que usaste, basada en tu `venv`).
2.  **Node.js y npm** (para el frontend React).
3.  **Google Maps API Key** (con "Distance Matrix API" y "Geocoding API" habilitadas).

### 2.1. Configuración del Backend (Python)

1.  Navega hasta la carpeta `backend/`.
2.  Crea y activa tu entorno virtual:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configuración de la API Key:** Edita tu archivo de configuración (ej: `.env` o `app/core/config.py`) e inserta tu clave de Google Maps.
5.  **Inicia el Servidor:**
    ```bash
    uvicorn app.main:app --reload
    ```
    (El servidor iniciará en `http://127.0.0.1:8000`).

### 2.2. Configuración del Frontend (React)

1.  Abre una **segunda terminal** y navega hasta la carpeta `frontend/`.
2.  Instala las dependencias:
    ```bash
    npm install
    ```
3.  Inicia la Aplicación React:
    ```bash
    npm start
    ```
    (El frontend abrirá en `http://localhost:3000`).

---

## 🧠 3. Explicación del Algoritmo de Optimización

Los detalles completos sobre la heurística y las reglas están en `ALGORITHM.md`, pero aquí está el resumen:

### 3.1. Algoritmo Elegido: Inserción Híbrida JIT (Just-in-Time)

Debido al volumen de datos (2.000 PDVs), una matriz de distancia completa sería muy costosa (alrededor de $660 USD por ejecución). El algoritmo resuelve esto en tres fases:

1.  **Filtro Geográfico (Haversine):** Para cada PDV, el sistema usa la fórmula Haversine (gratuita) para crear una lista de "Trabajadores Candidatos" (todos los que están dentro de un radio de 75 km).
2.  **Múltiples Pasadas (Agenda Semanal):** El algoritmo itera MÚLTIPLES veces (del 1º al 5º día) en la lista de PDVs para garantizar que todos los PDVs reciban el número correcto de visitas semanales (`visits_per_week`).
3.  **Inserción Optimizada (JIT):** Para cada PDV y para cada trabajador candidato, el sistema usa la heurística de **"Vecino Más Cercano" (Nearest Neighbor)**, pero con una mejura crucial:
    *   **Costo JIT:** El costo real del tiempo de viaje (`get_distance`) solo se consulta cuando el algoritmo necesita un par específico (A -> B). Verifica primero la caché de la BD y la memoria para ahorrar en la llamada a la API de Google.

### 3.2. Reglas de Negocio y Restricciones (Lo que el Código Garantiza)

| **Regla** | **Lógica de Cálculo** |
| --- | --- |
| **Asignación Justa** | El PDV se asigna al trabajador cuya ruta **ya existente** resulta en el menor `costo_adicional_desplazamiento` (tiempo de viaje). |
| **Límite de Tiempo** | La restricción se verifica solo contra el **Tiempo de la Visita** (ej: `visita_duration_seconds`). El tiempo de desplazamiento es **ignorado** en la verificación de capacidad diaria, garantizando que el PDV sea agendado incluso si el viaje es largo (según lo solicitado). |
| **Límite Diario** | El número de PDVs agendados por día no excede `max_visits_per_day`. |
| **Estado "Atendido"** | Un PDV solo se cuenta como **`total_pdvs_assigned`** si recibe el número completo de visitas requeridas (`visitas_per_week`). |

---

## 4. 🔗 Uso de la Aplicación (Flujo de Prueba)

Accede a `http://localhost:3000` y sigue el flujo:

1.  **POBLAR BD:** Usa la sección de Carga para enviar `Plantilla_Usuarios.csv` y `Plantilla_PDV.csv`.
2.  **INICIAR:** Haz clic en "Iniciar Generación de Rutas".
3.  **MONITOREAR:** El panel hará el *polling* de `GET /status/latest` y esperará hasta `COMPLETED`.
4.  **RESULTADOS:** La tabla se llenará con el `usuario_nombre` y la `Secuencia de PDVs asignados` por día de la semana (Lunes a Viernes).
5.  **DESCARGAR:** El botón "Descargar Excel" generará el archivo de resultados conteniendo `Hora de Llegada Estimada`, `Duración de la Visita`, y `Tiempo Total Acumulado`.