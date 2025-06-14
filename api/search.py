from flask import Blueprint, jsonify, request
from api.products import load_products

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    products = load_products()
    results = []
    
    for product in products:
        if (query in product['title'].lower() or 
            query in product.get('description', '').lower() or
            query in product.get('category', '').lower()):
            results.append(product)
    
    return jsonify(results) 