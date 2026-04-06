from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DetectedFood:
    name: str
    confidence: float


@dataclass
class PortionEstimate:
    name: str
    grams: float
    confidence: float
    range_label: str | None = None


class FoodVisionProvider(ABC):
    @abstractmethod
    def detect_foods(self, image_path: str) -> list[DetectedFood]:
        raise NotImplementedError

    @abstractmethod
    def estimate_portion(self, image_path: str, detected_foods: list[DetectedFood]) -> list[PortionEstimate]:
        raise NotImplementedError


class MockFoodVisionProvider(FoodVisionProvider):
    def detect_foods(self, image_path: str) -> list[DetectedFood]:
        base = image_path.lower()
        if "mixed" in base:
            return [
                DetectedFood(name="arroz", confidence=0.77),
                DetectedFood(name="pollo a la plancha", confidence=0.71),
                DetectedFood(name="ensalada", confidence=0.64),
            ]
        return [
            DetectedFood(name="pasta", confidence=0.74),
            DetectedFood(name="queso", confidence=0.56),
        ]

    def estimate_portion(self, image_path: str, detected_foods: list[DetectedFood]) -> list[PortionEstimate]:
        default_map = {
            "arroz": 150,
            "pollo a la plancha": 130,
            "ensalada": 90,
            "pasta": 200,
            "queso": 30,
        }
        results: list[PortionEstimate] = []
        for food in detected_foods:
            grams = default_map.get(food.name, 100)
            range_label = "mediano" if food.confidence < 0.7 else None
            results.append(
                PortionEstimate(name=food.name, grams=grams, confidence=max(food.confidence - 0.05, 0.4), range_label=range_label)
            )
        return results
