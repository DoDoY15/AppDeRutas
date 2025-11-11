# 🛣️ Route Optimization Application (VRP)

This project implements a robust solution for the Vehicle Routing Problem (VRP), calculating the optimal weekly schedule for a team of salespeople, minimizing travel time and respecting daily capacity constraints (work time and maximum number of visits).

The system is built with FastAPI (Python) for the backend and React/TypeScript for the frontend.

## 🎯 System Objective

The main goal is to transform two input data files (`Users` and `PDVs`) into an **optimized weekly schedule**, ensuring each PDV receives the correct number of weekly visits (Multiple Passes) and that travel time is minimized using real-time traffic data (Google Maps cache).

---

## ⚙️ 1. Deliverables and Structure

### 1.1. Repository Structure

```
/APP ROTAS
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core (configuration and security for potential scalability)
│   │   ├── crud/ (Upsert and DB Cache Logic)
│   │   ├── db/ (SQLAlchemy Models)
│   │   ├──  services/ (Algorithm and JIT API)
│   │   └── utils (for potential scalability)
│   ├── main.py
│   └── .env (or config.py)
│
├── frontend/
│   └── src/ (React/TSX Code)
│
└── README.md
```

💻 2. Installation and Execution Instructions

Prerequisites

1.  **Python 3.9+** (or the version you used, based on your `venv`).
2.  **Node.js and npm** (for the React frontend).
3.  **Google Maps API Key** (with "Distance Matrix API" and "Geocoding API" enabled).

### 2.1. Backend Configuration (Python)

1.  Navigate to the `backend/` folder.
2.  Create and activate your virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  **API Key Configuration:** Edit your configuration file (e.g., `.env` or `app/core/config.py`) and insert your Google Maps key.
5.  **Start the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    (The server will start at `http://127.0.0.1:8000`).

### 2.2. Frontend Configuration (React)

1.  Open a **second terminal** and navigate to the `frontend/` folder.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the React Application:
    ```bash
    npm start
    ```
    (The frontend will open at `http://localhost:3000`).

---

## 🧠 3. Optimization Algorithm Explanation

Full details about the heuristic and rules are in `ALGORITHM.md`, but here is the summary:

### 3.1. Chosen Algorithm: Hybrid JIT (Just-in-Time) Insertion

Due to the data volume (2,000 PDVs), a full distance matrix would be very expensive (around $660 USD per run). The algorithm solves this in three phases:

1.  **Geographic Filter (Haversine):** For each PDV, the system uses the Haversine formula (free) to create a list of "Candidate Workers" (all those within a 75 km radius).
2.  **Multiple Passes (Weekly Schedule):** The algorithm iterates MULTIPLE times (from the 1st to the 5th day) over the PDV list to ensure all PDVs receive the correct number of weekly visits (`visits_per_week`).
3.  **Optimized Insertion (JIT):** For each PDV and for each candidate worker, the system uses the **"Nearest Neighbor"** heuristic, but with a crucial improvement:
    *   **JIT Cost:** The actual travel time cost (`get_distance`) is only queried when the algorithm needs a specific pair (A -> B). It first checks the DB cache and memory to save on Google API calls.

### 3.2. Business Rules and Constraints (What the Code Guarantees)

| **Rule** | **Calculation Logic** |
| --- | --- |
| **Fair Assignment** | The PDV is assigned to the worker whose **existing** route results in the least `additional_travel_time_cost`. |
| **Time Limit** | The constraint is checked only against the **Visit Duration** (e.g., `visit_duration_seconds`). Travel time is **ignored** in the daily capacity check, ensuring the PDV is scheduled even if the trip is long (as requested). |
| **Daily Limit** | The number of PDVs scheduled per day does not exceed `max_visits_per_day`. |
| **"Served" Status** | A PDV is only counted as **`total_pdvs_assigned`** if it receives the full required number of visits (`visits_per_week`). |

---

## 4. 🔗 Application Usage (Testing Flow)

Access `http://localhost:3000` and follow the flow:

1.  **POPULATE DB:** Use the Upload section to send `Plantilla_Usuarios.csv` and `Plantilla_PDV.csv`.
2.  **START:** Click "Start Route Generation".
3.  **MONITOR:** The panel will poll `GET /status/latest` and wait until `COMPLETED`.
4.  **RESULTS:** The table will populate with the `user_name` and the `Assigned PDV Sequence` for each weekday (Monday to Friday).
5.  **DOWNLOAD:** The "Download Excel" button will generate the results file containing `Estimated Arrival Time`, `Visit Duration`, and `Total Accumulated Time`.
