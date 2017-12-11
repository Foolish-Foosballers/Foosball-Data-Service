from flask import Flask, jsonify, abort, request
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
import os, json, logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
from models import *

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)

def createTables():
    app.logger.debug('creating tables')
    db.create_all()
    app.logger.debug('created tables')

def dropTables():
    app.logger.debug('dropping tables')
    db.drop_all()
    app.logger.debug('dropped tables')

def jsonSerial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

@app.route('/')
def homepage():
    return """
    <h1>Welcome to the Foosball Data Service.</h1>
    <p>Here is a list of available routes:</p>
    <ul>
        <li><a href="/">/</a></li>
        <li><a href="/players">/players</a></li>
        <li><a>/players/&ltid&gt</a></li>
        <li><a>/players/&ltusername&gt</a></li>
        <li><a href="/games">/games</a></li>
        <li><a>/games/&ltid&gt</a></li>
    </ul>
    """

@app.route('/players')
def playersWithJsonify():
    return jsonify({'players': Player.query.all()})

@app.route('/players/<id>')
def playersById(id):
    player = Player.query.get_or_404(id)
    return json.dumps(player.as_dict(), default=jsonSerial)

@app.route('/players/<id>/jsonify')
def playersByIdJsonify(id):
    return jsonify({'player': Player.query.get(id)})

@app.route('/players', methods=['POST'])
def addPlayer():
    if not request.json:
        print "no json", request
        abort(400)
    for attribute in ['FirstName', 'LastName', 'Username', 'Email']: 
        if attribute not in request.json:
            print "no attribute", attribute
            abort(400)
    newPlayer = Player(request.json['FirstName'], request.json['LastName'], request.json['Username'], request.json['Email'])
    db.session.add(newPlayer)
    db.session.commit()
    return (jsonify({'player': player}), 201)

@app.route('/players/<username>')
def playersByUsername(username):
    player = Player.query.filter_by(Username=username).first_or_404()
    return json.dumps(player.as_dict(), default=jsonSerial)

@app.route('/players/<username>/jsonify')
def playersByUsernameJsonify(username):
    return jsonify({'player': Player.query.first(username)})

@app.route('/games')
def games():
    games = Game.query.all()
    return json.dumps([game.as_dict() for game in games], default=jsonSerial)

@app.route('/games/<id>')
def gamesById(id):
    game = Game.query.get_or_404(id)
    return json.dumps(player.as_dict(), default=jsonSerial)

if __name__ == '__main__':
    app.run()
