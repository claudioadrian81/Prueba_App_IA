# Contratos API (MVP)

Base URL: `http://localhost:8000`

## Auth
- `POST /api/auth/register`
  - body: `{ "email": "user@mail.com", "password": "secret123" }`
  - 200: `{ "access_token": "...", "token_type": "bearer" }`

- `POST /api/auth/login`
  - body: `{ "email": "user@mail.com", "password": "secret123" }`
  - 200: token JWT

## Meals
> Requieren header `Authorization: Bearer <token>`

- `POST /api/meals/analyze` (multipart)
  - field: `image` (jpg/png/webp, máx configurable)
  - 200:
    ```json
    {
      "job_id": 1,
      "meal_id": 10,
      "status": "completed",
      "confidence": 0.69,
      "needs_manual_review": true,
      "message": "Análisis completado. Revisa y corrige si es necesario."
    }
    ```

- `GET /api/meals/daily/summary?day=YYYY-MM-DD`
  - 200: resumen de calorías/macros del día + comidas.

- `GET /api/meals/{meal_id}`
  - 200: comida + `meal_items`.

- `PATCH /api/meals/{meal_id}/items/{item_id}`
  - body:
    - `{ "normalized_food_name": "arroz integral" }`
    - `{ "corrected_grams": 180 }`
    - `{ "remove": true }`

- `POST /api/meals/{meal_id}/items`
  - body: `{ "normalized_food_name": "manzana", "grams": 120 }`

- `GET /api/meals/disclaimer`
  - texto legal obligatorio.
