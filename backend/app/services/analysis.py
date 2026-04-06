from datetime import datetime

from sqlalchemy.orm import Session

from app.adapters.nutrition import NutritionProvider
from app.adapters.vision import FoodVisionProvider
from app.models.models import AnalysisJob, FoodCatalogCache, Meal, MealItem


class MealAnalysisService:
    def __init__(self, db: Session, vision: FoodVisionProvider, nutrition: NutritionProvider):
        self.db = db
        self.vision = vision
        self.nutrition = nutrition

    def analyze_meal(self, meal: Meal, job: AnalysisJob) -> tuple[Meal, bool]:
        detected = self.vision.detect_foods(meal.image_url)
        portions = self.vision.estimate_portion(meal.image_url, detected)

        meal.items.clear()
        needs_manual = False
        confidences = []

        total_cal = total_p = total_c = total_f = 0.0

        for portion in portions:
            nutrition_data = self._get_nutrition(portion.name)
            if not nutrition_data:
                needs_manual = True
                continue

            factor = portion.grams / 100.0
            calories = nutrition_data.calories_per_100g * factor
            protein = nutrition_data.protein_per_100g * factor
            carbs = nutrition_data.carbs_per_100g * factor
            fat = nutrition_data.fat_per_100g * factor
            confidence = round(portion.confidence, 2)
            confidences.append(confidence)

            if confidence < 0.65:
                needs_manual = True

            item = MealItem(
                meal_id=meal.id,
                detected_name=portion.name,
                normalized_food_name=nutrition_data.name,
                estimated_grams=portion.grams,
                calories=round(calories, 2),
                protein=round(protein, 2),
                carbs=round(carbs, 2),
                fat=round(fat, 2),
                confidence=confidence,
                was_user_corrected=False,
            )
            meal.items.append(item)
            total_cal += calories
            total_p += protein
            total_c += carbs
            total_f += fat

        meal.total_calories = round(total_cal, 2)
        meal.total_protein = round(total_p, 2)
        meal.total_carbs = round(total_c, 2)
        meal.total_fat = round(total_f, 2)
        meal.confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0
        meal.analyzed_at = datetime.utcnow()

        job.status = "completed"
        job.finished_at = datetime.utcnow()

        self.db.add(meal)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(meal)
        return meal, needs_manual

    def _get_nutrition(self, food_name: str):
        cached = self.db.query(FoodCatalogCache).filter(FoodCatalogCache.name == food_name.lower().strip()).first()
        if cached:
            return type(
                "CachedNutrition",
                (),
                {
                    "name": cached.name,
                    "calories_per_100g": cached.calories,
                    "protein_per_100g": cached.protein,
                    "carbs_per_100g": cached.carbs,
                    "fat_per_100g": cached.fat,
                },
            )()

        nutrition = self.nutrition.find_food(food_name)
        if not nutrition:
            return None

        cache_item = FoodCatalogCache(
            external_food_id=nutrition.external_food_id,
            source=nutrition.source,
            name=nutrition.name,
            serving_size=100,
            calories=nutrition.calories_per_100g,
            protein=nutrition.protein_per_100g,
            carbs=nutrition.carbs_per_100g,
            fat=nutrition.fat_per_100g,
            raw_payload=nutrition.raw_payload,
        )
        self.db.add(cache_item)
        self.db.flush()
        return nutrition
