import os
from flask import Blueprint, jsonify, request
from pathlib import Path
import json
import stripe

STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

confirm_bp = Blueprint('confirm', __name__)

@confirm_bp.route('/api/confirm', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.metadata.get('order_id')
        
        if order_id:
            orders_file = Path('orders/orders.json')
            if orders_file.exists():
                with open(orders_file) as f:
                    orders = json.load(f)
                for order in orders:
                    if order['order_id'] == order_id and order['status'] == 'pending':
                        order['status'] = 'paid'
                        order['payment_id'] = session.payment_intent
                with open(orders_file, 'w') as f:
                    json.dump(orders, f, indent=2)

    return jsonify({'status': 'success'}), 200 