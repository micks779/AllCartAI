from flask import Blueprint, jsonify, request
import json
from pathlib import Path
import requests

products_bp = Blueprint('products', __name__)

# Store registry (can be moved to a JSON file or DB later)
store_registry = {
    "oplente": {
        "type": "manual",
        "products_file": "products/oplente.products.json"
    },
    "test-shopify-store": {
        "type": "shopify",
        "products_url": "https://test-shopify-app.onrender.com/products"
    },
    "shopify-allcartai": {
        "type": "shopify",
        "products_url": "https://plugin-shopify-allcartai.onrender.com/api/products",
        "display_name": "AllCartAI Shopify Store"
    }
}

def get_available_brands():
    return list(store_registry.keys())

def load_products(brand=None):
    if not brand:
        # Return all products from all manual stores
        products = []
        for store, config in store_registry.items():
            if config["type"] == "manual":
                file_path = Path(config["products_file"])
                if file_path.exists():
                    with open(file_path) as f:
                        products.extend(json.load(f))
        return products
    config = store_registry.get(brand)
    if not config:
        return []
    if config["type"] == "manual":
        file_path = Path(config["products_file"])
        if file_path.exists():
            with open(file_path) as f:
                return json.load(f)
        return []
    elif config["type"] == "shopify":
        try:
            response = requests.get(config["products_url"], timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return []
    return []

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    brand = request.args.get('brand')
    if brand and brand not in get_available_brands():
        return jsonify({"error": "Invalid brand"}), 400
    products = load_products(brand)
    return jsonify(products)

@products_bp.route('/api/products/<store>', methods=['GET'])
def get_products_for_store(store):
    config = store_registry.get(store)
    if not config:
        return jsonify({"error": "Store not found"}), 404
    if config["type"] == "shopify":
        try:
            response = requests.get(config["products_url"], timeout=5)
            response.raise_for_status()
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": f"Failed to fetch Shopify products: {str(e)}"}), 500
    elif config["type"] == "manual":
        file_path = Path(config["products_file"])
        if file_path.exists():
            with open(file_path) as f:
                return jsonify(json.load(f))
        return jsonify([])
    return jsonify({"error": "Unknown store type"}), 400 