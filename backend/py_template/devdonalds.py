from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook: List[CookbookEntry] = []

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
def parse_handwriting(recipeName: str) -> Union[str | None]:
	nonletter = re.compile('[^a-zA-Z\\s]')
	return ' '.join(map(lambda x: x.capitalize(), nonletter.sub('', recipeName.replace('-', ' ').replace('_', ' ')).split())) or None


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	data = request.json
	for prev_entry in cookbook:
		if prev_entry.name == data["name"]: return 'Duplicate name', 400

	# Can't use match because I don't know if their machine uses 3.10+
	if data["type"] == "recipe":
		required_items: List[RequiredItem] = []
		for item in data["requiredItems"]:
			new_item = RequiredItem(item["name"], int(item["quantity"]))
			for prev_item in required_items:
				if new_item.name == prev_item.name: return 'Duplicate name', 400
			required_items.append(new_item)
		
		new_entry = Recipe(data["name"], required_items)
			
	elif data["type"] == "ingredient":
		new_entry = Ingredient(data["name"], int(data["cookTime"]))
		if new_entry.cook_time < 0: return 'Cannot have negative cook time!', 400

	else: return 'Invalid type!', 400

	cookbook.append(new_entry)

	return '', 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	# TODO: implement me
	return 'not implemented', 500


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
