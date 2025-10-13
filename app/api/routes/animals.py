"""
Endpoints CRUD for animals
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.enums.enum_race import Race
from app.enums.enum_status import Status
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class AnimalBase(BaseModel):
    """
    Schéma de base pour un animal.
    Contient les champs communs à la création et à la mise à jour.
    """

    name: str = Field(..., min_length=1, max_length=200, description="Nom de l'animal")
    race: Race = Field(..., description="Race de l'animal")
    status: Status = Field(..., description="Statut de l'animal")
    birth_date: int = Field(
        ..., ge=1000, le=datetime.now().year, description="Année de naissance de l'animal"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Adam de la Halle",
                "race": Race.CHICKEN,
                "status": 1,
                "published_year": 2003,
            }
        }
    )


class AnimalCreate(AnimalBase):
    """
    Schéma pour créer un nouvel animal.
    Hérite de AnimalBase, peut ajouter des champs spécifiques à la création.
    """

    pass


class AnimalUpdate(BaseModel):
    """
    Schéma pour mettre à jour un animal.
    Tous les champs sont optionnels (on peut modifier seulement certains champs).
    """

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    race: Optional[Race] = Field(None)
    status: Optional[Status] = Field(None)
    birth_date: Optional[int] = Field(None, ge=1000, le=datetime.now().year)


class Animal(AnimalBase):
    """
    Schéma complet d'un animal (avec ID).
    Utilisé pour les réponses de l'API.
    """

    id: int = Field(..., description="Identifiant unique d'un animal")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Adam de la Halle",
                "race": Race.CHICKEN,
                "status": 1,
                "birth_date": 2003,
                "created_at": "2024-01-15T10:30:00",
            }
        }
    )


animals_db: List[dict] = [
    {
        "id": 1,
        "name": "Obi-Wan CHICKENobi",
        "race": Race.CHICKEN,
        "status": 1,
        "birth_date": 2003,
        "created_at": datetime(2003, 1, 1, 10, 0, 0),
    },
    {
        "id": 2,
        "name": "CHICKEN-credible Ladies",
        "race": Race.CHICKEN,
        "status": 1,
        "birth_date": 2004,
        "created_at": datetime(2004, 1, 1, 10, 0, 0),
    },
    {
        "id": 3,
        "name": "CHICKEN-kerchief",
        "race": Race.CHICKEN,
        "status": 0,
        "birth_date": 1998,
        "created_at": datetime(1998, 1, 1, 10, 0, 0),
    },
    {
        "id": 4,
        "name": "Moo-gnificent",
        "race": Race.COW,
        "status": 1,
        "birth_date": 1975,
        "created_at": datetime(1975, 1, 1, 10, 0, 0),
    },
    {
        "id": 5,
        "name": "Moo-tiful",
        "race": Race.COW,
        "status": 1,
        "birth_date": 1975,
        "created_at": datetime(1975, 1, 1, 10, 0, 0),
    },
    {
        "id": 5,
        "name": "Cat-a-tonic",
        "race": Race.CAT,
        "status": 1,
        "birth_date": 2012,
        "created_at": datetime(2012, 1, 1, 10, 0, 0),
    },
]

NEXT_ID = 5


def find_animal_by_id(animal_id: int) -> Optional[dict]:
    """
    Recherche un animal par son ID

    Args:
        animal_id (int): L'identifiant de l'animal

    Returns:
        Optional[dict]: Animal si trouvé, None sinon
    """
    for animal in animals_db:
        if animal["id"] == animal_id:
            return animal
    return None


def find_animal_by_race(race: Race) -> Optional[dict]:
    """
    Recherche un animal selon sa race

    Args:
        race (str): Label de la race (ex: "Poule", insensible à la casse)

    Returns:
        Optional[dict]: Animal si trouvé, None sinon
    """
    race_enum = None
    for r in Race:
        if r.value.lower() == race.lower():
            race_enum = r
            break
    if not race_enum:
        return None
    for animal in animals_db:
        if animal["race"] == race_enum:
            return animal
    return None


def find_animal_by_name(name: str) -> Optional[dict]:
    """
    Recherche un animal selon son nom

    Args:
        name (str): Nom de l'animal

    Returns:
        Optional[dict]: Animal si trouvé, None sinon
    """
    for animal in animals_db:
        if animal["name"] == name:
            return animal
    return None


@router.get("/", response_model=List[Animal], status_code=status.HTTP_200_OK)
async def get_all_animals(status: Optional[bool] = None, race: Optional[str] = None):
    """
    Récupère la liste de tous les animaux.

    Paramètres de filtrage optionnels :
    - status: Filtrer par état (true = vivant/false = mort)
    - race: Filtrer par label de la race (recherche partielle, insensible à la casse)

    Returns:
        Liste des animaux correspondant aux critères
    """
    result = animals_db.copy()

    logger.info(f"GET /animals/ - Filtres: status={status}, race={race}")

    if status is not None:
        result = [animal for animal in result if animal["status"] == status]

    if race:
        race_enum = None
        for r in Race:
            if r.value.lower() == race.lower():
                race_enum = r
                break
        if not race_enum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"La race '{race}' n'existe pas."
            )
        result = [animal for animal in result if animal["race"] == race_enum]

    logger.info(f"Retour de {len(result)} animaux")

    return result


@router.get("/{animal_id}", response_model=Animal, status_code=status.HTTP_200_OK)
async def get_animal(animal_id: int):
    """
    Récupère les détails d'un animal spécifique par son ID.

    Args:
        animal_id: L'identifiant de l'animal

    Returns:
        Les informations complètes de l'animal

    Raises:
        HTTPException 404: Si l'animal n'existe pas
    """
    animal = find_animal_by_id(animal_id)

    if not animal:
        logger.warning(f"Animal {animal_id} non trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'animal avec l'ID {animal_id} n'existe pas",
        )

    logger.info(f"Animal {animal_id} trouvé: {animal['title']}")
    return animal


@router.post("/", response_model=Animal, status_code=status.HTTP_201_CREATED)
async def create_animal(animal: Animal):
    """
    Crée un nouvel animal dans la ferme.

    Args:
        animal: Les informations de l'animal à créer

    Returns:
        L'animal créé avec son ID et sa date de création

    Raises:
        HTTPException 400: Si un animal avec le même nom existe déjà
    """
    global NEXT_ID

    existing_animal = find_animal_by_name(animal.name)
    if existing_animal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un animal avec le nom {animal.name} existe déjà (ID: {existing_animal['id']})",
        )

    new_animal = {
        "id": NEXT_ID,
        **animal.model_dump(),
        "status": 1,
        "created_at": datetime.now(),
    }

    animals_db.append(new_animal)
    NEXT_ID += 1

    return new_animal


@router.put("/{animal_id}", response_model=Animal, status_code=status.HTTP_200_OK)
async def update_animal(animal_id: int, animal_update: AnimalUpdate):
    """
    Met à jour les informations d'un animal existant.
    Seuls les champs fournis sont modifiés.

    Args:
        animal_id: L'identifiant de l'animal à modifier
        animal_update: Les champs à mettre à jour

    Returns:
        L'animal mis à jour

    Raises:
        HTTPException 404: Si l'animal n'existe pas
        HTTPException 400: Si le nom modifié existe déjà sur un autre animal
    """
    animal = find_animal_by_id(animal_id)

    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'animal avec l'ID {animal_id} n'existe pas",
        )

    update_data = animal_update.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing_animal = find_animal_by_name(update_data["name"])
        if existing_animal and existing_animal["id"] != animal_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Un autre animal utilise déjà le nom {update_data['name']}",
            )

    animal.update(update_data)

    return animal


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(animal_id: int):
    """
    Supprime un animal de la ferme.

    Args:
        animal_id: L'identifiant de l'animal à supprimer

    Returns:
        Aucun contenu (code 204)

    Raises:
        HTTPException 404: Si l'animal n'existe pas
    """
    animal = find_animal_by_id(animal_id)

    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'animal avec l'ID {animal_id} n'existe pas",
        )
