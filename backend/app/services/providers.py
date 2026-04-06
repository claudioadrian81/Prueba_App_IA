from app.adapters.nutrition import MockNutritionProvider, NutritionProvider, USDAFoodDataProvider
from app.adapters.vision import FoodVisionProvider, MockFoodVisionProvider
from app.core.config import settings


def get_vision_provider() -> FoodVisionProvider:
    return MockFoodVisionProvider()


def get_nutrition_provider() -> NutritionProvider:
    if settings.nutrition_provider == "usda":
        return USDAFoodDataProvider(settings.usda_api_key)
    return MockNutritionProvider()
