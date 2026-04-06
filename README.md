# Meal Vision MVP (mobile-first)

MVP para registrar comidas a partir de fotos, estimar porciones/calorías/macros, mostrar confianza y permitir corrección manual.

## Stack
- **Frontend:** React + Vite responsive.
- **Backend:** FastAPI + SQLAlchemy + JWT.
- **DB:** PostgreSQL (docker) o SQLite local.
- **Storage:** local en desarrollo (`backend/uploads`).

## Estructura
- `frontend/` interfaz mobile-first.
- `backend/` API REST, modelo de datos, pipeline análisis mock.
- `docs/` arquitectura y contratos API.

## Modelo de datos
Tablas mínimas implementadas:
- `users`
- `meals`
- `meal_items`
- `food_catalog_cache`
- `analysis_jobs`

## Flujo MVP
1. Registro/login JWT.
2. Subir/tomar foto (input file).
3. Análisis (provider mock): detección + porción.
4. Enriquecimiento nutricional (mock + cache local).
5. Cálculo de calorías y macros por ítem/comida/día.
6. Revisión editable inline (nombre, gramos, eliminar; agregar por API).
7. Historial diario con total de calorías.

## Variables de entorno
Copiar `.env.example` a `.env`.

## Ejecución rápida con Docker
```bash
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

## Ejecución local sin Docker
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Seed de alimentos
```bash
cd backend
python -m app.main  # crea tablas por import
python scripts/seed.py
```

### Tests backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Endpoints principales
Ver `docs/api-contracts.md`.

## Mock e2e incluido
- Archivo de imagen con `mixed` en el nombre simula "plato mixto" (arroz + pollo + ensalada).
- Estado de análisis en curso visible en frontend.
- Mensaje de error si imagen no apta (tipo/tamaño).

## Disclaimer visible
La UI muestra un aviso permanente: estimación aproximada que **no reemplaza asesoramiento nutricional profesional**.

## Roadmap sugerido
- Integración real USDA FoodData Central.
- Provider de visión multimodal real.
- S3-compatible storage.
- Objetivos diarios y dashboard semanal.
- Varias fotos por comida y mejor referencia de escala.
