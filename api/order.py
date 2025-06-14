import os
from flask import Blueprint, jsonify, request
from api.products import get_available_brands, load_products
from datetime import datetime
from pathlib import Path
import json
import stripe

stripe.api_key = os.environ.get("STRIPE_API_KEY")

order_bp = Blueprint('order', __name__)

@order_bp.route('/api/order', methods=['POST'])
def place_order():
    try:
        order = request.json
        brand = order.get('brand')
        
        if not brand or brand not in get_available_brands():
            return jsonify({"error": "Invalid brand"}), 400

        # Load product catalog for the specific brand
        products = load_products(brand)

        # Check if product exists
        product = next((p for p in products if p['id'] == order['product_id']), None)
        if not product:
            return jsonify({"error": "Invalid product ID"}), 400

        # Create the order object
        new_order = {
            "order_id": f"ORD-{datetime.now().isoformat()}",
            "product_id": order["product_id"],
            "quantity": order["quantity"],
            "email": order["email"],
            "brand": brand,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }

        # Save order to file
        orders_file = Path('orders/orders.json')
        if orders_file.exists():
            with open(orders_file) as f:
                orders = json.load(f)
        else:
            orders = []

        orders.append(new_order)

        with open(orders_file, 'w') as f:
            json.dump(orders, f, indent=2)

        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': f"{product['title']} ({brand})",
                    },
                    'unit_amount': int(float(product['price']) * 100),
                },
                'quantity': order['quantity'],
            }],
            mode='payment',
            success_url='http://localhost:5000/success',
            cancel_url='http://localhost:5000/cancel',
            customer_email=order['email'],
            metadata={
                'brand': brand,
                'order_id': new_order['order_id']
            }
        )

        return jsonify({
            "message": "Order placed successfully!",
            "order_id": new_order["order_id"],
            "checkout_url": session.url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500 