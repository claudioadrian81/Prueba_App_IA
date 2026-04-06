# Arquitectura MVP

```
/frontend   -> React + Vite (mobile-first)
/backend    -> FastAPI + SQLAlchemy + JWT
/docs       -> contratos API y decisiones técnicas
```

## Flujo principal
1. Usuario inicia sesión/registro.
2. Sube foto desde frontend (`/api/meals/analyze`).
3. Backend valida imagen, guarda en storage local y crea `analysis_job`.
4. `MealAnalysisService` usa `FoodVisionProvider` + `NutritionProvider`.
5. Se persisten `meals` + `meal_items` + totales.
6. Frontend muestra revisión editable y resumen diario.

## Extensibilidad
- `FoodVisionProvider` desacopla proveedor mock/real multimodal.
- `NutritionProvider` permite mock o USDA FoodData Central.
- `FoodCatalogCache` reduce latencia y llamadas externas.
- Storage local preparado para swap futuro a S3-compatible.
