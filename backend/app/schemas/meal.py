from datetime import datetime

from pydantic import BaseModel, Field


class MealItemResponse(BaseModel):
    id: int
    detected_name: str
    normalized_food_name: str
    estimated_grams: float
    corrected_grams: float | None
    calories: float
    protein: float
    carbs: float
    fat: float
    confidence: float
    was_user_corrected: bool

    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    id: int
    image_url: str
    analyzed_at: datetime | None
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    confidence: float
    created_at: datetime
    items: list[MealItemResponse]

    class Config:
        from_attributes = True


class DaySummaryResponse(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meals: list[MealResponse]


class UpdateMealItemRequest(BaseModel):
    normalized_food_name: str | None = None
    corrected_grams: float | None = Field(default=None, gt=0)
    remove: bool = False


class AddMealItemRequest(BaseModel):
    normalized_food_name: str
    grams: float = Field(gt=0)


class AnalysisJobResponse(BaseModel):
    job_id: int
    meal_id: int
    status: str
    confidence: float
    needs_manual_review: bool
    message: str
