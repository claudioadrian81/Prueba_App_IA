from app.db.session import SessionLocal
from app.models.models import FoodCatalogCache

SEED = [
    ("mock-arroz", "mock", "arroz", 100, 130, 2.7, 28.0, 0.3),
    ("mock-pollo", "mock", "pollo a la plancha", 100, 165, 31.0, 0.0, 3.6),
    ("mock-ensalada", "mock", "ensalada", 100, 45, 1.5, 8.0, 0.6),
    ("mock-pasta", "mock", "pasta", 100, 157, 5.8, 30.9, 0.9),
    ("mock-manzana", "mock", "manzana", 100, 52, 0.3, 14.0, 0.2),
]


def main() -> None:
    db = SessionLocal()
    try:
        for ext_id, source, name, serving, cal, pro, carb, fat in SEED:
            exists = db.query(FoodCatalogCache).filter(FoodCatalogCache.name == name).first()
            if exists:
                continue
            db.add(
                FoodCatalogCache(
                    external_food_id=ext_id,
                    source=source,
                    name=name,
                    serving_size=serving,
                    calories=cal,
                    protein=pro,
                    carbs=carb,
                    fat=fat,
                    raw_payload={"seed": True},
                )
            )
        db.commit()
        print("Seed completed")
    finally:
        db.close()


if __name__ == "__main__":
    main()
