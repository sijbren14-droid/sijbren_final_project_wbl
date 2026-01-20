import json
from pathlib import Path
import requests
import random

ANIMALS_PATH = Path(__file__).parent.parent / "data" / "animals.json"
MEALS_PATH = Path(__file__).parent.parent / "data" / "meals.json"

def get_animal_image(animal):
    # 1. Eigen afbeelding
    if animal.get("image"):
        return f"/static/images/animals/{animal['image']}"

    # 2. Wikipedia backup
    wiki_query = animal.get("wiki") or animal.get("name")
    return get_wikipedia_image(wiki_query)


def get_wikipedia_image(query):
    url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "WhoWillBeLunch/1.0 (educational project)"
    }

    params = {
        "action": "query",
        "titles": query,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 400
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=5)
        data = r.json()

        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))

        return page.get(
            "thumbnail",
            {}
        ).get("source", "/static/images/placeholder.png")

    except Exception:
        return "/static/images/placeholder.png"

def get_animal_by_id(animal_id):
    animals = load_animals()
    meals = load_meals()

    animal = animals.get(animal_id)
    if not animal:
        return None

    animal = animal.copy()
    animal["meals"] = [meals[m] for m in animal["meals"] if m in meals]

    return animal


def load_animals():
    with open(ANIMALS_PATH, encoding="utf-8") as f:
        return json.load(f)

def load_meals():
    with open(MEALS_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_random_animal_with_meals():
    animals = load_animals()
    meals = load_meals()

    animal = random.choice(list(animals.values()))

    animal["meals"] = [meals[meal_id] for meal_id in animal["meals"]]

    return animal

def get_meal_by_id(meal_id):
    meals = load_meals()
    return meals.get(meal_id)

def get_all_animals():
    return load_animals().values()



