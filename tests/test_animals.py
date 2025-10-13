import pytest
from fastapi.testclient import TestClient

from app.api.init_db import init_db
from app.db import Base, engine
from app.enums.enum_race import Race
from app.main import app
from app.utils.logger import get_logger

client = TestClient(app)

logger = get_logger(__name__)


@pytest.fixture(autouse=True, scope="function")
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    init_db()

    yield

    Base.metadata.drop_all(bind=engine)


def test_get_all_animals():
    """
    Test que GET /animals retourne tous les animaux.
    """
    response = client.get("/animals/")

    assert response.status_code == 200
    animals = response.json()
    assert isinstance(animals, list)
    assert len(animals) == 6  # On a 6 animaux dans la DB initiale

    # Vérifier la structure du premier animal
    first_animal = animals[0]
    assert "id" in first_animal
    assert "name" in first_animal
    assert "race" in first_animal
    assert "status" in first_animal
    assert "birth_date" in first_animal


def test_get_animals_filter_by_race():
    response = client.get(
        "/animals/?race=Poule",
    )

    assert response.status_code == 200
    animals = response.json()
    assert isinstance(animals, list)
    assert len(animals) == 3  # On a 3 poules dans la DB initiale

    # Vérifier que toutes les poules ont le bon auteur
    for animal in animals:
        assert (
            animal["race"] == Race.CHICKEN.value
        )  # Vérifier qu'on a la bonne race pour tous les animaux
        # Vérifier la structure des animaux
        assert "id" in animal
        assert "name" in animal
        assert "race" in animal
        assert "status" in animal
        assert "birth_date" in animal
