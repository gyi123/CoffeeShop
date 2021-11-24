import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def getDrinks():
    selections = Drink.query.all()
    drinks = [drink.short() for drink in selections]
    return jsonify({
        'success':True,
        'drinks': drinks
        })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def getDrinks_Detail(payload):
    selections = Drink.query.all()
    drinks = [drink.long() for drink in selections]
    return jsonify({
        'success':True,
        'drinks': drinks
        })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def addDrink(payload):
    if not request.json:
        abort(400)
    body = request.json
    if ('title' not in body) or ('recipe' not in body):
        abort(422)
#check if recipe contain long information
    recipe = body['recipe']
    
    if isinstance(body['recipe'], dict):
        a = []
        a.append(recipe)
        recipe = a

    for ingridient in recipe:
        if('color' not in ingridient) or ('name' not in ingridient) or ('parts' not in ingridient ):
            abort(422)      
    drink = Drink(
        title = body['title'],
        recipe = json.dumps(recipe)
        )
    drink.insert()
    
    return jsonify({
            'success': True,
            'drinks': [drink.short()]
            })
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def updateDrink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    if not request.json:
        abort(400)
    body = request.json
   
    if ('title' not in body) and ('recipe' not in body):
        abort(422)
#check if recipe contain long information
    if 'recipe' in body:
        for ingridient in body['recipe']:
            if('color' not in ingridient) or ('name' not in ingridient) or ('parts' not in ingridient ):
                abort(422)
        drink['recipe'] = json.dumps(body['recipe'])
    if 'title' not in body:
        drink['title'] = body['title']
    drink.update()
    
    return jsonify({
            'success': True,
            'drinks': [drink.short()]
            })    

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrink(payload,id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    drink.delete()
    
    return jsonify({
            'success': True,
            'delete': id
            })    

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def error_404(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404
    )
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def autherror(error):
    return (
        jsonify({"success": False, "error": error.status_code, "message": error.error}),
            error.status_code
    )
