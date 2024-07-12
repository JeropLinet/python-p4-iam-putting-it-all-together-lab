#!/usr/bin/env python3

from flask import request, session , make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data=request.get_json()
        username=data.get('username')
        password=data.get('password')
        image_url=data.get('image_url')
        bio=data.get('bio')

        if not username or not password:
            return {'error':'Username and Password are required'},422
        
        new_user=User(
            username=username,
            image_url=image_url,
            bio=bio,
        )

        new_user.password_hash=password

        try:
         db.session.add(new_user)
         db.session.commit()
        except IntegrityError:
           db.session.rollback()
           return {'error':'Username already exists'},400
        return{'message':'User created successfully'},201
    
    

class CheckSession(Resource):
    def get(self):
        user_id=session.get('user_id')
        if user_id:
            user=User.query.filter(User.id ==user_id).first()
            return user.to_dict(),200
        return {'error':'Unauthorised.'},401
        

class Login(Resource):
    def post(self):
        data=request.get_json()
        username=data.get('username')
        password=data.get('password')

        user=User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id']=user.id
            return make_response(user.to_dict(),200)
        return {'error':'Invalid username or password'},401

class Logout(Resource):
    def delete(self):
        user_id=session.get('user_id')
        if user_id is None:
            return make_response({'error':'Unauthorized.'},401)
        session.clear()
        return {},204
        

class RecipeIndex(Resource):
    def get(self):
        user_id=session.get('user_id')
        if user_id:
            recipes=Recipe.query.filter_by(user_id=user_id).all()
            return make_response([recipe.to_dict()for recipe in recipes],200)
        return make_response({'error':'Unauthorized'},401)
    
    def post(self):
        user_id=session.get('user_id')
        if not user_id:
            return {'error':'Unauthorized'},401
        
        data=request.get_json()
        title=data.get('title')
        instructions=data.get('instructions')
        minutes_to_complete=data.get('minutes_to_complete')

        if not title or not instructions or len(instructions)<50:
            return {'error':'Title and Instructions must be present with at least 50 characters'},422
        
        new_recipe=Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user_id,
        )

        db.session.add(new_recipe)
        db.session.commit()
        response=new_recipe.to_dict()
        return response,201

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)