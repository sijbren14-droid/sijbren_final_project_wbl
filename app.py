#aanmaken app: https://flask.palletsprojects.com/en/latest/quickstart/
#gebruik templates: https://flask.palletsprojects.com/en/latest/templating/
#verbinding database: https://docs.python.org/3/library/pathlib.html
#limiet op submisions: https://flask-limiter.readthedocs.io/en/stable/#

from flask import Flask, render_template, request, redirect
from flask import session
import re
import json
from pathlib import Path
from werkzeug.utils import secure_filename

from services.meal_service import get_meal_image
from services.animal_service import get_animal_image
from services.animal_service import (
    get_random_animal_with_meals,
    get_animal_by_id,
    get_meal_by_id,
    load_meals,
    load_animals
)

from flask import Flask, render_template, request, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
UPLOAD_FOLDER = "static/images/meals"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# -------------------------------------------------
# PATHS
# -------------------------------------------------
ANIMALS_PATH = Path("data/animals.json")
MEALS_PATH = Path("data/meals.json")
PENDING_ANIMALS_PATH = Path("data/pending_animals.json")
PENDING_MEALS_PATH = Path("data/pending_meals.json")

# -------------------------------------------------
# GENERIC HELPERS
# -------------------------------------------------
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text

def add_meals(animal_id, animals, meals):
    children = []

    animal = animals.get(animal_id)
    if not animal:
        return children

    for meal_id in animal.get("meals", []):
        if meal_id in meals:
            meal = meals[meal_id]
            children.append({
                "id": f"{animal_id}__{meal_id}",
                "name": meal["name"],
                "image": get_meal_image(meal),
                "children": []
            })

    return children

def build_meal_nodes(animal_id, animals, meals):
    meal_nodes = []

    animal = animals.get(animal_id)
    if not animal:
        return meal_nodes

    for meal_id in animal.get("meals", []):
        if meal_id in meals:
            meal = meals[meal_id]
            meal_nodes.append({
                "id": f"{animal_id}__{meal_id}",
                "name": meal["name"],
                "image": get_meal_image(meal),
                "children": []
            })

    return meal_nodes


# -------------------------------------------------
# FOOD WEB – DATA MODEL
# -------------------------------------------------
def make_node(item_id, animals, meals):
    if item_id in animals:
        a = animals[item_id]
        return {
            "id": a["id"],
            "name": a["name"],
            "image": get_animal_image(a),
            "children": []
        }

    if item_id in meals:
        m = meals[item_id]
        return {
            "id": m["id"],
            "name": m["name"],
            "image": get_meal_image(m),
            "children": []
        }

    return {
        "id": item_id,
        "name": item_id,
        "image": "/static/images/placeholder.jpg",
        "children": []
    }

def build_food_tree(root_id, animals, meals):
    root = make_node(root_id, animals, meals)

    root_animal = animals.get(root_id)
    if not root_animal:
        return root

    for prey_id in root_animal.get("meals", []):

        # -------------------------
        # CASE 1: prey is een DIER
        # -------------------------
        if prey_id in animals:
            prey_node = make_node(prey_id, animals, meals)


            prey_node["children"] = build_meal_nodes(
                prey_id, animals, meals
            )

            root["children"].append(prey_node)

        # -------------------------
        # CASE 2: prey is een MEAL
        # -------------------------
        elif prey_id in meals:
            meal = meals[prey_id]
            root["children"].append({
                "id": f"{root_id}__{prey_id}",
                "name": meal["name"],
                "image": get_meal_image(meal),
                "children": []
            })

    return root


# -------------------------------------------------
# FOOD WEB – LAYOUT ENGINE (PROCEDURAL)
# -------------------------------------------------
START_X = 400
START_Y = 600

H_SPACING = 600
V_SPACING = 170

DEPTH_X_OFFSET = -80
DEPTH_Y_OFFSET = 20     
SPREAD_FACTOR = 0.2     


def layout_tree(root, animals):
    nodes = []
    edges = []
    layers = {}

    
    def collect(node, depth=0):
        layers.setdefault(depth, []).append(node)

        for child in node.get("children", []):
            edges.append({
                "from": node["id"],
                "to": child["id"]
            })
            collect(child, depth + 1)

    collect(root)

    
    for depth, layer_nodes in layers.items():
        base_x = START_X + depth * H_SPACING
        count = len(layer_nodes)

        center_index = (count - 1) / 2
        dynamic_spacing = V_SPACING + (count * SPREAD_FACTOR * DEPTH_Y_OFFSET)

        total_height = (count - 1) * dynamic_spacing
        start_y = START_Y - total_height / 2

        for i, node in enumerate(layer_nodes):
            distance = abs(i - center_index)

            x = base_x + distance * DEPTH_X_OFFSET
            y = (
                start_y
                + i * dynamic_spacing
                + (distance * DEPTH_Y_OFFSET)
                - (distance * DEPTH_Y_OFFSET / 2)
            )

            nodes.append({
                "id": node["id"],
                "name": node["name"],
                "image": node["image"],
                "x": x,
                "y": y,
                "depth": depth,

                "type": "animal" if node["id"] in animals else "meal"
            })

    return nodes, edges


# -------------------------------------------------
# ROUTES – PUBLIC
# -------------------------------------------------
@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/menu")
def menu():
    animal_id = request.args.get("animal_id")

    animal = (
        get_animal_by_id(animal_id)
        if animal_id
        else get_random_animal_with_meals()
    )

    if not animal:
        return "Animal not found", 404

    animal["image_url"] = get_animal_image(animal)

    meals_db = load_meals()
    meals_full = []
    meals = load_meals()

    for meal_item in animal.get("meals", []):
        if isinstance(meal_item, dict):
            meal = meal_item.copy()
        else:
            meal = meals_db.get(meal_item)
            if not meal:
                continue
            meal = meal.copy()

        meal["image_url"] = get_meal_image(meal)
        meals_full.append(meal)

    animal["meals_full"] = meals_full

    return render_template(
        "menu.html",
        animal=animal,
        all_animals=load_animals().values(),
        all_meals=meals.values(),
        selected_animal_id=animal_id
        
    )

@app.route("/meal/<meal_id>")
def meal_detail(meal_id):
    meal = get_meal_by_id(meal_id)
    meal["image_url"] = get_meal_image(meal)
    return render_template("meal.html", meal=meal)


# -------------------------------------------------
# FOOD WEB ROUTE
# -------------------------------------------------
@app.route("/food-web/<animal_id>")
def food_web(animal_id):
    animals = load_animals()
    meals = load_meals()

    tree = build_food_tree(animal_id, animals, meals)
    if not tree:
        return "Food web niet gevonden", 404

    nodes, edges = layout_tree(tree, animals)

    animal = animals.get(animal_id)

    return render_template(
        "food_web.html",
        nodes=nodes,
        edges=edges,
        animal_id=animal_id,
        animal_name=animal["name"] if animal else animal_id
    )

# ------------------
# SUBMIT ANIMAL
# ------------------
def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text


@app.route("/submit-animal", methods=["POST"])
@limiter.limit("5 per minute")
def submit_animal():
    pending_animals = load_json(PENDING_ANIMALS_PATH)
    pending_meals = load_json(PENDING_MEALS_PATH)

    name = request.form.get("name", "").strip()
    if not name:
        return redirect("/submit-animal")

    animal_id = slugify(name)
    diet = request.form.get("diet") or None
    description = request.form.get("description", "").strip()
    meals = request.form.getlist("meals")

    # nieuw gerecht
    new_meal_name = request.form.get("new_meal_name", "").strip()
    new_meal_type = request.form.get("new_meal_type")
    new_meal_description = request.form.get("new_meal_description", "").strip()

    if new_meal_name:
        new_meal_id = slugify(new_meal_name)

        pending_meals[new_meal_id] = {
            "id": new_meal_id,
            "name": new_meal_name,
            "type": new_meal_type,
            "description": new_meal_description,
            "image": None,
            "wiki": None,
        }

        meals.append(new_meal_id)

    pending_animals[animal_id] = {
        "id": animal_id,
        "name": name,
        "diet": diet,
        "description": description,
        "meals": meals,
        "approved": False,
        "image": None,
        "wiki": None,
    }

    save_json(PENDING_ANIMALS_PATH, pending_animals)
    save_json(PENDING_MEALS_PATH, pending_meals)

    return redirect("/")
 

# ------------------
# ADMIN
# ------------------
@app.route("/admin")
def admin():
    pending_animals = load_json(PENDING_ANIMALS_PATH)
    pending_meals = load_json(PENDING_MEALS_PATH)
    animals = load_json(ANIMALS_PATH)
    meals = load_json(MEALS_PATH)

    return render_template(
        "admin.html",
        pending_animals=pending_animals,
        pending_meals=pending_meals,
        animals=animals,
        meals=meals,
    )


# ------------------
# APPROVE / REJECT ANIMAL
# ------------------
@app.route("/approve-animal/<animal_id>")
def approve_animal(animal_id):
    animals = load_json(ANIMALS_PATH)
    pending = load_json(PENDING_ANIMALS_PATH)

    if animal_id in pending:
        animals[animal_id] = pending.pop(animal_id)
        save_json(ANIMALS_PATH, animals)
        save_json(PENDING_ANIMALS_PATH, pending)

    return redirect("/admin")


@app.route("/reject-animal/<animal_id>")
def reject_animal(animal_id):
    pending = load_json(PENDING_ANIMALS_PATH)
    pending.pop(animal_id, None)
    save_json(PENDING_ANIMALS_PATH, pending)
    return redirect("/admin")


@app.route("/reject-animal_e/<animal_id>")
def reject_animal_existing(animal_id):
    animals = load_json(ANIMALS_PATH)
    animals.pop(animal_id, None)
    save_json(ANIMALS_PATH, animals)
    return redirect("/admin")


# ------------------
# APPROVE / REJECT MEAL
# ------------------
@app.route("/approve-meal/<meal_id>")
def approve_meal(meal_id):
    meals = load_json(MEALS_PATH)
    pending = load_json(PENDING_MEALS_PATH)

    if meal_id in pending:
        meals[meal_id] = pending.pop(meal_id)
        save_json(MEALS_PATH, meals)
        save_json(PENDING_MEALS_PATH, pending)

    return redirect("/admin")


@app.route("/reject-meal/<meal_id>")
def reject_meal(meal_id):
    pending = load_json(PENDING_MEALS_PATH)
    pending.pop(meal_id, None)
    save_json(PENDING_MEALS_PATH, pending)
    return redirect("/admin")


# ------------------
# EDIT EXISTING ANIMAL
# ------------------
@app.route("/admin/animals/<animal_id>/edit", methods=["GET", "POST"])
def edit_animal(animal_id):
    animals = load_animals()
    meals = load_meals()

    animal = animals.get(animal_id)
    if not animal:
        return "Animal not found", 404

    if request.method == "POST":
        animal["name"] = request.form.get("name", "").strip()
        animal["diet"] = request.form.get("diet") or None
        animal["description"] = request.form.get("description", "").strip()
        animal["wiki"] = request.form.get("wiki", "").strip() or None
        animal["meals"] = request.form.getlist("meals")

        if request.form.get("remove_image") == "1":
            animal["image"] = None

        image = request.files.get("image")
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(f"static/images/animals/{filename}")
            animal["image"] = filename

        save_json(ANIMALS_PATH, animals)
        return redirect("/admin")

    animal["image_url"] = get_animal_image(animal)

    return render_template(
        "admin_edit_animal.html",
        animal=animal,
        all_meals=meals.values(),
    )


# ------------------
# EDIT EXISTING MEAL
# ------------------
@app.route("/admin/meals/<meal_id>/edit", methods=["GET", "POST"])
def edit_meal(meal_id):
    meals = load_json(MEALS_PATH)
    meal = meals.get(meal_id)

    if not meal:
        return "Meal not found", 404

    if request.method == "POST":
        meal["name"] = request.form["name"].strip()
        meal["type"] = request.form["type"]
        meal["description"] = request.form.get("description", "").strip()
        meal["wiki"] = request.form.get("wiki", "").strip() or None

        if request.form.get("remove_image") == "1":
            meal["image"] = None

        file = request.files.get("image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = Path("static/images/meals") / filename
            file.save(save_path)
            meal["image"] = filename

        save_json(MEALS_PATH, meals)
        return redirect("/admin")

    meal["image_url"] = get_meal_image(meal)

    return render_template("admin_edit_meal.html", meal=meal)


# ------------------
# ADD NEW ANIMAL
# ------------------
@app.route("/admin/animals/new", methods=["GET", "POST"])
def admin_add_animal():
    animals = load_animals()
    meals = load_meals()

    if request.method == "POST":
        animal_id = request.form["id"].strip().lower()
        animals[animal_id] = {
            "id": animal_id,
            "name": request.form["name"].strip(),
            "diet": request.form.get("diet") or None,
            "meals": request.form.getlist("meals"),
        }
        save_json(ANIMALS_PATH, animals)
        return redirect("/admin")

    return render_template(
        "admin_add_animal.html",
        all_meals=meals.values(),
    )


# ------------------
# ADD NEW MEAL
# ------------------
@app.route("/admin/meals/new", methods=["GET", "POST"])
def admin_add_meal():
    meals = load_meals()

    if request.method == "POST":
        meal_id = request.form["id"].strip().lower()
        meals[meal_id] = {
            "id": meal_id,
            "name": request.form["name"].strip(),
            "type": request.form["type"],
            "description": request.form.get("description", "").strip(),
            "image": None,
        }
        save_json(MEALS_PATH, meals)
        return redirect("/admin")

    return render_template("admin_add_meal.html")

# --------------------END-----------------------------
if __name__ == "__main__":
    app.run(debug=True)