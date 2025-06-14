from flask import Blueprint, jsonify, request
import json
from pathlib import Path

products_bp = Blueprint('products', __name__)

def get_available_brands():
    """Get list of available brands from product files."""
    products_dir = Path('products')
    return [f.stem.replace('.products', '') for f in products_dir.glob('*.products.json')]

def load_products(brand=None):
    """Load products from a specific brand or all brands."""
    products = []
    products_dir = Path('products')
    
    if brand:
        file_path = products_dir / f"{brand}.products.json"
        if file_path.exists():
            with open(file_path) as f:
                products.extend(json.load(f))
    else:
        for file_path in products_dir.glob('*.products.json'):
            with open(file_path) as f:
                products.extend(json.load(f))
    
    return products

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    brand = request.args.get('brand')
    if brand and brand not in get_available_brands():
        return jsonify({"error": "Invalid brand"}), 400
    
    products = load_products(brand)
    return jsonify(products) 