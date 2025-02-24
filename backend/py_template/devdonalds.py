from dataclasses import dataclass
from typing import Counter, List, Dict, Tuple, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class Recipe:
	required_items: Counter[str]

@dataclass
class Ingredient:
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook: Dict[str, Recipe | Ingredient] = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that
regex = re.compile("[^a-zA-Z\\s]")
def parse_handwriting(recipeName: str) -> Union[str | None]:
	recipeName = recipeName.replace('-', ' ').replace('_', ' ')
	recipeName = regex.sub('', recipeName)
	return ' '.join(map(str.capitalize, recipeName.split())) or None


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	data = request.json

	name = data["name"]
	if name in cookbook: return 'Duplicate name', 400

	# Can't use match because I don't know if their machine uses Python 3.10+
	# E.g., My Debian VPS comes with 3.9
	if data["type"] == "recipe":
		required_items: Counter[str] = Counter()
		for item in data["requiredItems"]:
			if item["name"] in required_items: return 'Duplicate name', 400
			required_items[item["name"]] = item["quantity"]
		
		cookbook[name] = Recipe(required_items)
			
	elif data["type"] == "ingredient":
		cook_time = data["cookTime"]
		if cook_time < 0: return 'Negative cook time', 400

		cookbook[name] = Ingredient(cook_time)

	else: return 'Invalid type', 400

	return '', 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name

def get_summary(name: str) -> Tuple[int, Counter[str]] | None:
	if name not in cookbook: return None
	entry = cookbook[name]

	if isinstance(entry, Recipe):
		total_time = 0
		total_ingredients: Counter[str] = Counter()

		for (item_name, quantity) in entry.required_items.items():
			item_time_and_ingredients = get_summary(item_name)
			if item_time_and_ingredients is None: return None
			item_time, item_ingredients = item_time_and_ingredients

			total_time += quantity * item_time
			item_ingredients = Counter({
				name: quantity * item_quantity 
				for name, item_quantity in item_ingredients.items()
			})
			total_ingredients.update(item_ingredients)
		
		return total_time, total_ingredients

	elif isinstance(entry, Ingredient):
		return entry.cook_time, Counter({name: entry.cook_time})

@app.route('/summary', methods=['GET'])
def summary():
	entry_name = request.args["name"]
	if entry_name in cookbook and isinstance(cookbook[entry_name], Ingredient):
		return 'Ingredient', 400

	entry_summary = get_summary(entry_name)

	if entry_summary is None: return '', 400
	time, ingredients = entry_summary

	return {
		"name": entry_name,
		"cookTime": time,
		"ingredients": [{
			"name": ingredient,
			"quantity": quantity
		} for ingredient, quantity in ingredients.items()]
	}, 200


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
