from datetime import datetime

from sqlalchemy.orm import Session

from app.api.models.animal import Animal
from app.db import SessionLocal
from app.enums.enum_race import Race
from app.enums.enum_status import Status


def init_db():
    db: Session = SessionLocal()
    try:
        db.query(Animal).delete()
        db.commit()

        animals_data = [
            Animal(
                name="Obi-Wan Henobi",
                race=Race.CHICKEN.value,
                status=Status.ALIVE.value,
                birth_date=2003,
                created_at=datetime(2003, 1, 1, 10, 0, 0),
            ),
            Animal(
                name="Hen-credible Ladies",
                race=Race.CHICKEN.value,
                status=Status.ALIVE.value,
                birth_date=2004,
                created_at=datetime(2004, 1, 1, 10, 0, 0),
            ),
            Animal(
                name="Hen-kerchief",
                race=Race.CHICKEN.value,
                status=Status.DEAD.value,
                birth_date=1998,
                created_at=datetime(1998, 1, 1, 10, 0, 0),
            ),
            Animal(
                name="Moo-gnificent",
                race=Race.COW.value,
                status=Status.ALIVE.value,
                birth_date=1975,
                created_at=datetime(1975, 1, 1, 10, 0, 0),
            ),
            Animal(
                name="Moo-tiful",
                race=Race.COW.value,
                status=Status.ALIVE.value,
                birth_date=1975,
                created_at=datetime(1975, 1, 1, 10, 0, 0),
            ),
            Animal(
                name="Cat-a-tonic",
                race=Race.CAT.value,
                status=Status.ALIVE.value,
                birth_date=2012,
                created_at=datetime(2012, 1, 1, 10, 0, 0),
            ),
        ]

        db.add_all(animals_data)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
