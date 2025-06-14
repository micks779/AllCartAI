from flask import Flask, send_file
from api.products import products_bp
from api.search import search_bp
from api.order import order_bp
from api.confirm import confirm_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(products_bp)
app.register_blueprint(search_bp)
app.register_blueprint(order_bp)
app.register_blueprint(confirm_bp)

@app.route('/success')
def payment_success():
    return '''
    <html>
    <head>
        <title>Payment Success</title>
        <style>
            body { background: #f6fff6; font-family: Arial, sans-serif; text-align: center; padding-top: 80px; }
            .success-box {
                display: inline-block;
                background: #e6ffe6;
                border: 2px solid #4CAF50;
                border-radius: 12px;
                padding: 40px 30px;
                box-shadow: 0 2px 12px rgba(76,175,80,0.08);
            }
            .success-icon {
                font-size: 60px;
                color: #4CAF50;
            }
            h1 { color: #333; margin-bottom: 10px; }
            p { color: #555; font-size: 18px; }
        </style>
    </head>
    <body>
        <div class="success-box">
            <div class="success-icon">✅</div>
            <h1>Thank you! Your order was successful.</h1>
            <p>We've received your payment and your order is being processed.<br>Check your email for confirmation and next steps.</p>
        </div>
    </body>
    </html>
    '''

@app.route('/.well-known/ai-plugin.json')
def plugin_manifest():
    return send_file('.well-known/ai-plugin.json', mimetype='application/json')

@app.route('/openapi.yaml')
def openapi_spec():
    return send_file('openapi.yaml', mimetype='text/yaml')

if __name__ == '__main__':
    app.run(debug=True)
