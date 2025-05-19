from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:secret@postgres:5432/main'
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

def verify_token(token):
    response = requests.post(
        'http://auth:5000/verify',
        headers={'Authorization': token}
    )
    return response.status_code == 200

# Новый метод для просмотра заказа
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return jsonify({'message': 'Unauthorized'}), 401
    
    order = Order.query.get(order_id)
    if order:
        return jsonify({
            'id': order.id,
            'item': order.item,
            'quantity': order.quantity
        }), 200
    return jsonify({'message': 'Order not found'}), 404

@app.route('/create_order', methods=['POST'])
def create_order():
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return jsonify({'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    order = Order(item=data['item'], quantity=data['quantity'])
    db.session.add(order)
    db.session.commit()
    return jsonify({'id': order.id}), 201

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    token = request.headers.get('Authorization')
    if not verify_token(token):
        return jsonify({'message': 'Unauthorized'}), 401
    
    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted'}), 200
    return jsonify({'message': 'Order not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)