"""
Endpoints CRUD for animals
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from app.api.models.animal import Animal as AnimalModel
from app.db import SessionLocal
from app.enums.enum_race import Race
from app.enums.enum_status import Status
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

    @field_validator("race", mode="before")
    @classmethod
    def parse_race(cls, v):
        if isinstance(v, Race):
            return v
        try:
            return Race(v)
        except ValueError:
            for r in Race:
                if hasattr(r, "label") and r.label.lower() == str(v).lower():
                    return r
            raise

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, v):
        if isinstance(v, Status):
            return v
        try:
            return Status(v)
        except ValueError:
            raise

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Adam de la Halle",
                "race": Race.CHICKEN,
                "status": 1,
                "birth_date": 2003,
                "created_at": "2024-01-15T10:30:00",
            }
        },
    )


def find_animal_by_id(db: Session, animal_id: int) -> Optional[Animal]:
    """
    Recherche un animal par son ID dans la base de données

    Args:
        db (Session): Session SQLAlchemy de la base de données
        animal_id (int): L'identifiant de l'animal

    Returns:
        Animal | None: L'animal trouvé ou None si aucun animal trouvé
    """
    return db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()


def find_animals_by_race(db: Session, race: str) -> List[Animal]:
    """
    Recherche des animaux selon une race (label insensible à la casse)

    Args:
        db (Session): Session SQLAlchemy de la base de données
        race (str): Label de la race (ex: "Poule", insensible à la casse)

    Returns:
        List[Animal]: Liste d'animaux trouvé ou None si aucun animal trouvé
    """
    race_enum = None
    for r in Race:
        if r.value.lower() == race.lower() or r.name.lower() == race.lower():
            race_enum = r
            break
    if not race_enum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"La race '{race}' n'existe pas."
        )
    animals = db.query(AnimalModel).filter(AnimalModel.race == race_enum.value).all()
    if len(animals) == 0:
        return []
    return [Animal.model_validate(animal) for animal in animals]


def find_animal_by_name(db: Session, name: str) -> Optional[Animal]:
    """
    Recherche un animal selon son nom

    Args:
        db (Session): Session SQLAlchemy de la base de données.
        name (str): Nom de l'animal

    Returns:
        Animal | None: Animal trouvé ou None si aucun animal trouvé
    """
    animal = db.query(AnimalModel).filter(AnimalModel.name == name).first()
    if animal is None:
        return None
    return animal


@router.get("/", response_model=List[Animal], status_code=status.HTTP_200_OK)
async def get_all_animals(
    status: Optional[int] = None, race: Optional[str] = None, db: Session = Depends(get_db)
):
    """
    Récupère la liste de tous les animaux.

    Paramètres de filtrage optionnels :
    - status: Filtrer par état (true = vivant/false = mort)
    - race: Filtrer par label de la race (recherche partielle, insensible à la casse)

    Args:
        db (Session): Session SQLAlchemy de la base de données

    Returns:
        Liste des animaux correspondant aux critères
    """
    query = db.query(AnimalModel)

    logger.info(f"GET /animals/ - Filtres: status={status}, race={race}")

    if status is not None:
        query = query.filter(AnimalModel.status == status)

    if race:
        race_enum = None
        for r in Race:
            if (
                r.value.lower() == race.lower()
                or r.name.lower() == race.lower()
                or (hasattr(r, "label") and r.label.lower() == race.lower())
            ):
                race_enum = r
                break

        if not race_enum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"La race '{race}' n'existe pas."
            )
        query = query.filter(AnimalModel.race == race_enum.value)
    result = query.all()

    logger.info(f"Retour de {len(result)} animaux")
    if len(result) == 0:
        return []
    return [Animal.model_validate(animal) for animal in result]


@router.get("/{animal_id}", response_model=Animal, status_code=status.HTTP_200_OK)
async def get_animal(animal_id: int, db: Session = Depends(get_db)):
    """
    Récupère les détails d'un animal spécifique par son ID.

    Args:
        animal_id: L'identifiant de l'animal
        db (Session): Session SQLAlchemy de la base de données

    Returns:
        Les informations complètes de l'animal

    Raises:
        HTTPException 404: Si l'animal n'existe pas
    """
    animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()

    if not animal:
        logger.warning(f"Animal {animal_id} non trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'animal avec l'ID {animal_id} n'existe pas",
        )

    logger.info(f"Animal {animal_id} trouvé: {animal.name}")
    return Animal.model_validate(animal)


@router.post("/", response_model=Animal, status_code=status.HTTP_201_CREATED)
async def create_animal(animal: AnimalCreate, db: Session = Depends(get_db)):
    """
    Crée un nouvel animal dans la ferme.

    Args:
        animal: Les informations de l'animal à créer
        db (Session): Session SQLAlchemy de la base de données

    Returns:
        L'animal créé avec son ID et sa date de création

    Raises:
        HTTPException 400: Si un animal avec le même nom existe déjà
        HTTPException 400: Si la race n'existe pas
    """

    existing_animal = db.query(AnimalModel).filter(AnimalModel.name == animal.name).first()
    if existing_animal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un animal avec le nom {animal.name} existe déjà (ID: {existing_animal.id})",
        )

    race_enum = None
    for r in Race:
        if (
            r.value.lower() == animal.race.value.lower()
            or r.name.lower() == animal.race.value.lower()
        ):
            race_enum = r
            break
    if not race_enum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"La race '{animal.race}' n'existe pas."
        )

    db_animal = AnimalModel(
        name=animal.name,
        race=race_enum.value,
        status=animal.status.value,
        birth_date=animal.birth_date,
        created_at=datetime.now(),
    )
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return Animal.model_validate(db_animal)


@router.put("/{animal_id}", response_model=Animal, status_code=status.HTTP_200_OK)
async def update_animal(animal_id: int, animal_update: AnimalUpdate, db: Session = Depends(get_db)):
    """
    Met à jour les informations d'un animal existant.
    Seuls les champs fournis sont modifiés.

    Args:
        animal_id: L'identifiant de l'animal à modifier
        animal_update: Les champs à mettre à jour
        db (Session): Session SQLAlchemy de la base de données

    Returns:
        L'animal mis à jour

    Raises:
        HTTPException 404: Si l'animal n'existe pas
        HTTPException 400: Si le nom modifié existe déjà sur un autre animal
         HTTPException 400: Si la race n'existe pas
    """
    animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()

    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'animal avec l'ID {animal_id} n'existe pas",
        )

    update_data = animal_update.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_animal = (
            db.query(AnimalModel).filter(AnimalModel.name == update_data["name"]).first()
        )
        if existing_animal and existing_animal.id != animal_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Un autre animal utilise déjà le nom {update_data['name']}",
            )

    if "race" in update_data and update_data["race"] is not None:
        race_enum = None
        for r in Race:
            if (
                r.value.lower() == update_data["race"].value.lower()
                or r.name.lower() == update_data["race"].value.lower()
            ):
                race_enum = r
                break
        if not race_enum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La race '{update_data['race']}' n'existe pas.",
            )
        update_data["race"] = race_enum.value

    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = update_data["status"].value

    for key, value in update_data.items():
        setattr(animal, key, value)

    db.commit()
    db.refresh(animal)
    return Animal.model_validate(animal)


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    """
    Supprime un animal de la ferme.

    Args:
        animal_id: L'identifiant de l'animal à supprimer
        db (Session): Session SQLAlchemy de la base de données

    Returns:
        Aucun contenu (code 204)

    Raises:
        HTTPException 404: Si l'animal n'existe pas
    """
    animal = find_animal_by_id(db, animal_id)

    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"L'animal avec l'ID {animal_id} n'existe pas",
        )

    db.delete(animal)
    db.commit()
