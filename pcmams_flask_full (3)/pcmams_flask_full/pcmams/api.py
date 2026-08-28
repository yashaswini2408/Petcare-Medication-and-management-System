
from flask import Blueprint, jsonify, request
from .models import Pet, User, Adoption
from . import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/pets', methods=['GET'])
def api_pets():
    pets = Pet.query.all()
    return jsonify([{'id':p.id,'name':p.name,'species':p.species,'age':p.age,'image':p.image} for p in pets])

@api_bp.route('/pets', methods=['POST'])
def api_create_pet():
    data = request.json or {}
    pet = Pet(name=data.get('name','Unnamed'), species=data.get('species'), age=data.get('age'), image=data.get('image'), description=data.get('description'))
    db.session.add(pet)
    db.session.commit()
    return jsonify({'status':'ok','id':pet.id}), 201

@api_bp.route('/adoptions', methods=['GET'])
def api_adoptions():
    ads = Adoption.query.all()
    return jsonify([{'id':a.id,'user_id':a.user_id,'pet_id':a.pet_id,'status':a.status} for a in ads])
