# Ferme API

A FastAPI project for managing animals in a farm.  
This API allows you to create, read, update, and delete animals, as well as filter them by race and status.

## Features

- CRUD endpoints for animals
- Filter animals by race or status
- Enum-based validation for race and status
- SQLAlchemy ORM for database management
- Pydantic models for data validation
- Logging for API actions
- Pytest-based test suite

## Deployment
The project was deployed on render [here](https://m1-python-rendu.onrender.com/), and you can access the doc [here](https://m1-python-rendu.onrender.com/docs)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Rendu
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Set up the database:**
   The database will be created automatically when you run the app.

2. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access the API documentation:**
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## API Endpoints

- `GET /animals/` — List all animals (with optional filters)
- `GET /animals/{animal_id}` — Get details of a specific animal
- `POST /animals/` — Create a new animal
- `PUT /animals/{animal_id}` — Update an animal
- `DELETE /animals/{animal_id}` — Delete an animal

## Testing

Run the test suite with:
```bash
pytest
```

## Project Structure

```
app/
  api/
    routes/
      animals.py
    models/
      animal.py
    init_db.py
  db.py
  enums/
    enum_race.py
    enum_status.py
  utils/
    logger.py
  main.py
tests/
  test_animals.py
README.md
requirements.txt
```

## License

MIT License