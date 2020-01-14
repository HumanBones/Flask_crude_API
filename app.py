from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError
import os
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


app.config['SECRET_KEY'] = 'thisissecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)


    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty


class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'qty')


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args,**kwargs)
    return decorator

@app.route('/product', methods=['POST'])
@token_required
def add_product():

    valid_values = ['name','description','price', 'qty']
    errors = []


    for key in valid_values:
        if not request.json.get(key):
            errors.append(f"Key {key} is required!")
    
    if not isinstance(request.json.get('price'), (float)):
        errors.append("Price must be a float!")

    if not isinstance(request.json.get('description'), (str)):
        errors.append("Description must be a string!")

    if not isinstance(request.json.get('name'),(str)):
        errors.append('Name must be a string!')
    
    if not isinstance(request.json.get('qty'), (int)):
        errors.append("Qty must be an integer")
    
    qty = request.json.get('qty')
    if qty is not None and qty < 0:
        errors.append("qty must be a positiv number or 0")


    if errors:
        response = jsonify({"errors": errors})
        response.status_code = 400 

        return response

    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']


    new_product = Product(name, description, price, qty)

    try:
        db.session.add(new_product)
        db.session.commit()
        return product_schema.jsonify(new_product), 201
    
    except IntegrityError:
        db.session.rollback()
        response = jsonify("Product already exists!")
        response.status_code = 400

        return response

    #return product_schema.jsonify(new_product),201


@app.route('/product', methods=['GET'])
@token_required
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)



@app.route('/product/<id>', methods=['GET'])
@token_required
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)



@app.route('/product/<id>', methods=['PUT'])
@token_required
def update_product(id):
    product = Product.query.get(id)
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    errors = []

    
    if not isinstance(name,(str)):
        errors.append("Name must be a string!")

    if not isinstance(description, (str)):
        errors.append("Description must be a string!")

    if not isinstance(price, (float)):
        errors.append("Price must be a float!")

    if not isinstance(qty, (int)):
        errors.append("Qty must be a integer!")
    
    if qty < 0:
        errors.append("Qty must be a positiv number or 0")
    
    if errors:
        response = jsonify({"errors": errors})
        response.status_code = 400 

        return response
    

    product.name = name
    product.description = description
    product.price = price
    product.qty = qty

    db.session.commit()

    return product_schema.jsonify(product)


@app.route('/product/<id>', methods=['DELETE'])
@token_required
def delete_product(id):
    product = Product.query.get(id)
    if product is None:
        response = jsonify("Error product not found!")
        response.status_code = 400
        
        return response
    
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)


@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'password':
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})
    
    elif not auth or not auth.username or not auth.password:
        response = jsonify('Username and password required!')
        response.statuse_code = 400
        return response


    response = jsonify('Could not verify, wrong username or password!')
    response.status_code = 401
    return response

if __name__ == "__main__":
    app.run(debug=True)
