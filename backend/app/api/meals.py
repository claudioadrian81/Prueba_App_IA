from datetime import date, datetime, time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.models import AnalysisJob, Meal, MealItem, User
from app.schemas.common import MessageResponse
from app.schemas.meal import (
    AddMealItemRequest,
    AnalysisJobResponse,
    DaySummaryResponse,
    MealResponse,
    UpdateMealItemRequest,
)
from app.services.analysis import MealAnalysisService
from app.services.auth import get_current_user
from app.services.providers import get_nutrition_provider, get_vision_provider
from app.services.storage import LocalImageStorage

router = APIRouter(prefix="/api/meals", tags=["meals"])
storage = LocalImageStorage()


@router.post("/analyze", response_model=AnalysisJobResponse)
def analyze_meal(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if image.content_type not in settings.allowed_image_types_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de imagen no soportado")

    image.file.seek(0, 2)
    size = image.file.tell()
    image.file.seek(0)
    if size > settings.max_image_size_mb * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Imagen supera tamaño permitido")

    image_path = storage.save(image)

    meal = Meal(user_id=current_user.id, image_url=image_path)
    db.add(meal)
    db.flush()

    job = AnalysisJob(meal_id=meal.id, provider=settings.food_vision_provider, status="processing")
    db.add(job)
    db.commit()
    db.refresh(meal)
    db.refresh(job)

    service = MealAnalysisService(db, get_vision_provider(), get_nutrition_provider())
    meal, needs_manual = service.analyze_meal(meal, job)

    return AnalysisJobResponse(
        job_id=job.id,
        meal_id=meal.id,
        status=job.status,
        confidence=meal.confidence,
        needs_manual_review=needs_manual,
        message="Análisis completado. Revisa y corrige si es necesario.",
    )


@router.get("/daily/summary", response_model=DaySummaryResponse)
def get_daily_summary(day: date | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target = day or datetime.utcnow().date()
    start = datetime.combine(target, time.min)
    end = datetime.combine(target, time.max)

    meals = (
        db.query(Meal)
        .filter(and_(Meal.user_id == current_user.id, Meal.created_at >= start, Meal.created_at <= end))
        .order_by(Meal.created_at.desc())
        .all()
    )

    return DaySummaryResponse(
        date=str(target),
        total_calories=round(sum(m.total_calories for m in meals), 2),
        total_protein=round(sum(m.total_protein for m in meals), 2),
        total_carbs=round(sum(m.total_carbs for m in meals), 2),
        total_fat=round(sum(m.total_fat for m in meals), 2),
        meals=meals,
    )


@router.get("/{meal_id}", response_model=MealResponse)
def get_meal(meal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meal = db.query(Meal).filter(and_(Meal.id == meal_id, Meal.user_id == current_user.id)).first()
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return meal


@router.patch("/{meal_id}/items/{item_id}", response_model=MealResponse)
def update_meal_item(
    meal_id: int,
    item_id: int,
    payload: UpdateMealItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meal = db.query(Meal).filter(and_(Meal.id == meal_id, Meal.user_id == current_user.id)).first()
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")

    item = db.query(MealItem).filter(and_(MealItem.id == item_id, MealItem.meal_id == meal.id)).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if payload.remove:
        db.delete(item)
    else:
        if payload.normalized_food_name:
            item.normalized_food_name = payload.normalized_food_name.lower().strip()
            item.was_user_corrected = True
        if payload.corrected_grams:
            item.corrected_grams = payload.corrected_grams
            item.was_user_corrected = True

        grams = item.corrected_grams or item.estimated_grams
        ratio = grams / (item.estimated_grams or grams)
        item.calories = round(item.calories * ratio, 2)
        item.protein = round(item.protein * ratio, 2)
        item.carbs = round(item.carbs * ratio, 2)
        item.fat = round(item.fat * ratio, 2)

    _recalculate_meal_totals(meal)
    db.commit()
    db.refresh(meal)
    return meal


@router.post("/{meal_id}/items", response_model=MealResponse)
def add_meal_item(
    meal_id: int,
    payload: AddMealItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meal = db.query(Meal).filter(and_(Meal.id == meal_id, Meal.user_id == current_user.id)).first()
    if not meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")

    nutrition = get_nutrition_provider().find_food(payload.normalized_food_name)
    if not nutrition:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alimento no encontrado")

    factor = payload.grams / 100
    item = MealItem(
        meal_id=meal.id,
        detected_name=payload.normalized_food_name,
        normalized_food_name=nutrition.name,
        estimated_grams=payload.grams,
        corrected_grams=payload.grams,
        calories=round(nutrition.calories_per_100g * factor, 2),
        protein=round(nutrition.protein_per_100g * factor, 2),
        carbs=round(nutrition.carbs_per_100g * factor, 2),
        fat=round(nutrition.fat_per_100g * factor, 2),
        confidence=0.5,
        was_user_corrected=True,
    )
    db.add(item)
    _recalculate_meal_totals(meal)
    db.commit()
    db.refresh(meal)
    return meal


@router.get("/disclaimer", response_model=MessageResponse)
def disclaimer():
    return MessageResponse(
        message=(
            "Este estimador es aproximado y no reemplaza asesoramiento nutricional profesional. "
            "La precisión depende de la calidad de la foto y porción visible."
        )
    )


def _recalculate_meal_totals(meal: Meal) -> None:
    totals = {"cal": 0.0, "pro": 0.0, "carb": 0.0, "fat": 0.0, "conf": []}
    for item in meal.items:
        totals["cal"] += item.calories
        totals["pro"] += item.protein
        totals["carb"] += item.carbs
        totals["fat"] += item.fat
        totals["conf"].append(item.confidence)

    meal.total_calories = round(totals["cal"], 2)
    meal.total_protein = round(totals["pro"], 2)
    meal.total_carbs = round(totals["carb"], 2)
    meal.total_fat = round(totals["fat"], 2)
    meal.confidence = round(sum(totals["conf"]) / len(totals["conf"]), 2) if totals["conf"] else 0
    meal.analyzed_at = datetime.utcnow()
