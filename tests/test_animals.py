from services.animal_service import (
    get_all_animals,
    load_animals,
    load_meals,
    get_random_animal_with_meals,
    get_animal_by_id
)

from services.meal_service import get_meal_image
from services.animal_service import get_animal_image
from app import build_food_tree, layout_tree


# -------------------------
# IMAGE RESOLUTION
# -------------------------
def test_animal_image_resolves():
    animal = get_random_animal_with_meals()
    image = get_animal_image(animal)

    assert image is not None
    assert isinstance(image, str)

    # image moet of lokaal of extern zijn
    assert (
        image.startswith("/static/")
        or image.startswith("http://")
        or image.startswith("https://")
    )


def test_meal_image_resolves():
    meals = load_meals()
    meal = next(iter(meals.values()))

    image = get_meal_image(meal)

    assert image is not None
    assert image.startswith("/static/")


# -------------------------
# FOOD TREE STRUCTURE
# -------------------------
def test_food_tree_builds_root():
    animals = load_animals()
    meals = load_meals()

    root_id = next(iter(animals.keys()))
    tree = build_food_tree(root_id, animals, meals)

    assert tree is not None
    assert tree["id"] == root_id
    assert "children" in tree
    assert isinstance(tree["children"], list)


def test_food_tree_children_have_ids():
    animals = load_animals()
    meals = load_meals()

    root_id = next(iter(animals.keys()))
    tree = build_food_tree(root_id, animals, meals)

    for child in tree["children"]:
        assert "id" in child
        assert "name" in child
        assert "image" in child


def test_food_tree_no_infinite_loops():
    animals = load_animals()
    meals = load_meals()

    root_id = next(iter(animals.keys()))
    tree = build_food_tree(root_id, animals, meals)

    visited = set()

    def walk(node):
        assert node["id"] not in visited
        visited.add(node["id"])
        for c in node.get("children", []):
            walk(c)

    walk(tree)


# -------------------------
# LAYOUT ENGINE
# -------------------------
def test_layout_produces_nodes_and_edges():
    animals = load_animals()
    meals = load_meals()

    root_id = next(iter(animals.keys()))
    tree = build_food_tree(root_id, animals, meals)

    nodes, edges = layout_tree(tree)

    assert isinstance(nodes, list)
    assert isinstance(edges, list)
    assert len(nodes) > 0


def test_all_nodes_have_coordinates():
    animals = load_animals()
    meals = load_meals()

    root_id = next(iter(animals.keys()))
    tree = build_food_tree(root_id, animals, meals)

    nodes, _ = layout_tree(tree)

    for node in nodes:
        assert "x" in node
        assert "y" in node
        assert isinstance(node["x"], (int, float))
        assert isinstance(node["y"], (int, float))


def test_edges_reference_existing_nodes():
    animals = load_animals()
    meals = load_meals()

    root_id = next(iter(animals.keys()))
    tree = build_food_tree(root_id, animals, meals)

    nodes, edges = layout_tree(tree)
    node_ids = {n["id"] for n in nodes}

    for edge in edges:
        assert edge["from"] in node_ids
        assert edge["to"] in node_ids


# -------------------------
# EDGE CASES
# -------------------------
def test_unknown_animal_returns_none():
    animal = get_animal_by_id("dit-bestaat-niet")
    assert animal is None


def test_animal_without_meals_does_not_crash():
    animals = load_animals()
    meals = load_meals()

    # fake dier zonder meals
    animals["test_dier"] = {
        "id": "test_dier",
        "name": "Test Dier",
        "meals": []
    }

    tree = build_food_tree("test_dier", animals, meals)
    assert tree is not None
    assert tree["children"] == []

def test_animals_loaded():
    animals = list(get_all_animals())
    assert len(animals) > 0


def test_load_animals_returns_dict():
    animals = load_animals()
    assert isinstance(animals, dict)


def test_load_meals_returns_dict():
    meals = load_meals()
    assert isinstance(meals, dict)


def test_get_random_animal():
    animal = get_random_animal_with_meals()

    assert animal is not None
    assert "id" in animal
    assert "meals" in animal
    assert isinstance(animal["meals"], list)
    assert len(animal["meals"]) > 0


def test_get_specific_animal():
    animal = get_animal_by_id("paard")

    assert animal is not None
    assert animal["id"] == "paard"
    assert isinstance(animal["meals"], list)


def test_animal_has_valid_meals():
    animal = get_random_animal_with_meals()

    for meal in animal["meals"]:
        assert "id" in meal
        assert "name" in meal
        assert "type" in meal
