from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NutritionData:
    source: str
    external_food_id: str
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    raw_payload: dict


class NutritionProvider(ABC):
    @abstractmethod
    def find_food(self, food_name: str) -> NutritionData | None:
        raise NotImplementedError


class MockNutritionProvider(NutritionProvider):
    MOCK_DB = {
        "arroz": (130, 2.7, 28.0, 0.3),
        "pollo a la plancha": (165, 31.0, 0.0, 3.6),
        "ensalada": (45, 1.5, 8.0, 0.6),
        "pasta": (157, 5.8, 30.9, 0.9),
        "queso": (402, 25.0, 1.3, 33.0),
        "manzana": (52, 0.3, 14.0, 0.2),
    }

    def find_food(self, food_name: str) -> NutritionData | None:
        key = food_name.lower().strip()
        vals = self.MOCK_DB.get(key)
        if not vals:
            return None
        calories, protein, carbs, fat = vals
        return NutritionData(
            source="mock",
            external_food_id=f"mock-{key}",
            name=key,
            calories_per_100g=calories,
            protein_per_100g=protein,
            carbs_per_100g=carbs,
            fat_per_100g=fat,
            raw_payload={"mock": True},
        )


class USDAFoodDataProvider(NutritionProvider):
    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def find_food(self, food_name: str) -> NutritionData | None:
        # Placeholder for progressive real integration.
        return None
