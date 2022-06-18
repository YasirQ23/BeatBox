# from app.models import MarvelCharacters, db, Colections
# from .services import token_required
# from flask import Blueprint, jsonify, request
# from flask_login import current_user

# api = Blueprint('api', __name__, url_prefix='/api')


# @api.route('/marvelcharacters', methods=['GET'])
# def getMarvelCharacters():
#     marvelcharacter = MarvelCharacters.query.all()
#     marvelcharacter = {a.id: a.to_dict() for a in marvelcharacter}
#     return jsonify(marvelcharacter), 200


# @api.route('/marvelcharacters/<string:name>', methods=['GET'])
# def MarvelCharactersName(name):

#     marvelcharacters = MarvelCharacters.query.filter_by(
#         name=name.title()).first()
#     if marvelcharacters:
#         return jsonify(marvelcharacters.to_dict()), 200
#     return jsonify({'error': f'no such marvel character with the name: {name.title()}'}), 404


# @api.route('/create', methods=['POST'])
# @token_required
# def createMarvelCharacters():
#     try:
#         newdict = request.get_json()
#         a = MarvelCharacters(newdict)
#     except:
#         return jsonify({'error': 'improper request or body data'}), 400
#     try:
#         db.session.add(a)
#         db.session.commit()
#     except:
#         return jsonify({'error': 'marvel character already exists in the database'}), 400
#     return jsonify({'created': a.to_dict()}), 200

# @api.route('/update/<string:id>', methods=['POST'])
# @token_required
# def updateMarvelCharacter(id):
#     try:
#         newvals = request.get_json()
#         character = MarvelCharacters.query.get(id)
#         character.from_dict(newvals)
#         db.session.commit()
#         return jsonify({'Updated marvel character': character.to_dict()}), 200
#     except:
#         return jsonify({'Request failed': 'Invalid request or marvel character ID does not exist.'}), 400


# @api.route('/delete/<string:id>', methods=['DELETE'])
# @token_required
# def removeMarvelCharacter(id):
#     character = MarvelCharacters.query.get(id)
#     if not character:
#         return jsonify({'Remove failed': f'No marvel character with ID {id} in the database.'}), 404
#     db.session.delete(character)
#     db.session.commit()
#     return jsonify({'Removed character': character.to_dict()}), 200
