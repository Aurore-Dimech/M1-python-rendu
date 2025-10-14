import pytest
from fastapi.testclient import TestClient

from app.api.init_db import init_db
from app.db import Base, engine
from app.enums.enum_race import Race
from app.enums.enum_status import Status
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
    """
    Test que GET /animals avec un filtre utilisé sur la query retourne tous les animaux correspondant au filtre
    """
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


def test_get_animal_by_id():
    """
    Test que GET /animals/{animal_id} retourne l'animal correspondant à l'ID donné
    """
    response_all = client.get("/animals/")
    animal_id = response_all.json()[0][
        "id"
    ]  # Prendre l'ID du premier animal existant dans notre base de données

    response = client.get(f"/animals/{animal_id}")

    assert response.status_code == 200
    animal = response.json()
    assert animal["id"] == animal_id
    assert "id" in animal
    assert "name" in animal
    assert "race" in animal
    assert "status" in animal
    assert "birth_date" in animal

    # Test avec un ID n'étant lié à aucun animal dans notre base de données
    non_existent_response = client.get("/animals/999")
    assert non_existent_response.status_code == 404
    assert "detail" in non_existent_response.json()
    assert "n'existe pas" in non_existent_response.json()["detail"]


def test_create_animal():
    """
    Test que POST /animals/ crée un animal
    """
    new_animal_data = {
        "name": "New Animal",
        "race": Race.CHICKEN.value,
        "status": Status.ALIVE.value,
        "birth_date": 2022,
    }

    response = client.post("/animals/", json=new_animal_data)

    assert response.status_code == 201
    created_animal = response.json()
    assert "id" in created_animal
    assert created_animal["name"] == "New Animal"
    assert created_animal["race"] == Race.CHICKEN.value
    assert created_animal["status"] == Status.ALIVE.value
    assert created_animal["birth_date"] == 2022

    # Test avec un nom déjà utilisé
    duplicate_response = client.post("/animals/", json=new_animal_data)
    assert duplicate_response.status_code == 400
    assert "existe déjà" in duplicate_response.json()["detail"]


def test_update_animal():
    """
    Test que PUT /animals/{animal_id} met à jour un animal existant
    """
    response_all = client.get("/animals/")
    animal_id = response_all.json()[0]["id"]

    update_data = {
        "name": "Updated Name",
        "race": Race.DOG.value,
    }

    response = client.put(f"/animals/{animal_id}", json=update_data)

    assert response.status_code == 200
    updated_animal = response.json()
    assert updated_animal["id"] == animal_id
    assert updated_animal["name"] == "Updated Name"
    assert updated_animal["race"] == Race.DOG.value

    # Test avec un ID n'étant lié à aucun animal dans notre base de données
    non_existent_response = client.put("/animals/999", json=update_data)
    assert non_existent_response.status_code == 404


def test_delete_animal():
    """
    Test que DELETE /animals/{animal_id} supprime un animal de notre base de données
    """
    response_all = client.get("/animals/")
    animal_id = response_all.json()[0]["id"]

    response = client.delete(f"/animals/{animal_id}")

    assert response.status_code == 204

    check_response = client.get(f"/animals/{animal_id}")
    assert check_response.status_code == 404

    # Test avec un ID n'étant lié à aucun animal dans notre base de données
    non_existent_response = client.delete("/animals/999")
    assert non_existent_response.status_code == 404
