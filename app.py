from flask import Flask, abort, request, jsonify
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

    if isinstance(obj, enum.Enum):
        return obj.value

    raise TypeError ("Type %s not serializable" % type(obj))

####################
# GET                           
####################

@app.route('/')
def homepage():
    createTables()
    return """
    <h1>Welcome to the Foosball Data Service.</h1>
    <p>Here is a list of available routes for reading data:</p>
    <ul>
        <li><a href="/">/</a></li>
        <li><a href="/players">/players</a></li>
        <li><a>/players/&ltid&gt</a></li>
        <li><a>/players/&ltusername&gt</a></li>
        <li><a href="/games">/games</a></li>
        <li><a>/games/&ltid&gt</a></li>
        <li><a href="/series">/series</a></li>
        <li><a href="/history">/history></a></li>
    </ul>
    """

@app.route('/players', methods=['GET'])
def getPlayers():
    players = Players.query.all()
    return json.dumps([player.as_dict() for player in players], default=jsonSerial)

@app.route('/players/<int:id>', methods=['GET'])
def getPlayerById(id):
    player = Players.query.get_or_404(id)
    return json.dumps(player.as_dict(), default=jsonSerial)

@app.route('/players/<username>', methods=['GET'])
def getPlayerByUsername(username):
    player = Players.query.filter_by(Username=username).first_or_404()
    return json.dumps(player.as_dict(), default=jsonSerial)

@app.route('/games', methods=['GET'])
def getGames():
    games = Games.query.all()
    return json.dumps([game.as_dict() for game in games], default=jsonSerial)

@app.route('/games/<int:id>', methods=['GET'])
def getGameById(id):
    game = Games.query.get_or_404(id)
    return json.dumps(player.as_dict(), default=jsonSerial)

@app.route('/series', methods=['GET'])
def getSeries():
    series = Series.query.all()
    return json.dumps([match.as_dict() for match in series], default=jsonSerial)

@app.route('/history', methods=['GET'])
def getHistory():
    history = History.query.all()
    return json.dumps([entry.as_dict() for entry in history], default=jsonSerial)

####################
# POST 
####################

@app.route('/players', methods=['POST'])
def createPlayer():
    if not request.json:
        abort(400)
    for attribute in ['FirstName', 'LastName', 'Username', 'Email']: 
        if attribute not in request.json:
            abort(400)
    newPlayer = Players(request.json['FirstName'], 
                        request.json['LastName'], 
                        request.json['Username'], 
                        request.json['Email'])
    db.session.add(newPlayer)
    db.session.commit()
    return (json.dumps(newPlayer.as_dict(), default=jsonSerial), 201)

@app.route('/games', methods=['POST'])
def createGame():
    if not request.json:
        abort(400)
    for attribute in ['Single', 'LeftScore', 'RightScore', 'WinMargin', 'Winner']: # add EndTime later
        if attribute not in request.json:
            abort(400)
    if request.json['Winner'] not in ('Left', 'Right'):
        abort(400)
    
    newGame = Games(request.json['Single'],
                    request.json['LeftScore'],
                    request.json['RightScore'],
                    request.json['WinMargin'],
                    TableSide.LEFT if request.json['Winner'] == 'Left' else TableSide.RIGHT)
    db.session.add(newGame)
    db.session.commit()
    return (json.dumps(newGame.as_dict(), default=jsonSerial), 201)

@app.route('/series', methods=['POST'])
def createSeries():
    if not request.json:
        abort(400)
    for attribute in ['NumGames', 'LeftWins', 'RightWins']: # might not be necessary
        if attribute not in request.json:
            abort(400)
    newSeries = Series(request.json['NumGames'],
                       request.json['LeftWins'],
                       request.json['RightWins'])
    db.session.add(newSeries)
    db.session.commit()
    return (json.dumps(newSeries.as_dict(), default=jsonSerial), 201)

@app.route('/history', methods=['POST'])
def createHistory():
    if not request.json:
        abort(400)
    for attribute in ['GameId', 'PlayerId', 'SeriesId', 'Side']:
        if attribute not in request.json:
            abort(400)
    newHistory = History(request.json['GameId'],
                         request.json['PlayerId'],
                         request.json['SeriesId'],
                         TableSide.LEFT if request.json['Side'] == 'Left' else TableSide.RIGHT)
    db.session.add(newHistory)
    db.session.commit()
    return (json.dumps(newHistory.as_dict(), default=jsonSerial), 201)

####################
# DELETE 
####################

@app.route('/players/<int:id>', methods=['DELETE'])
def removePlayerById(id):
    db.session.delete(Players.query.get(id))
    db.session.commit()
    return jsonify({ 'result': True }) 

@app.route('/games/<int:id>', methods=['DELETE'])
def removeGameById(id):
    db.session.delete(Games.query.get(id))
    db.session.commit()
    return jsonify({ 'result': True })

@app.route('/series/<int:id>', methods=['DELETE'])
def removeSeriesById(id):
    db.session.delete(Series.query.get(id))
    db.session.commit()
    return jsonify({ 'result': True })

# TODO: figure out how to access history by primary key and delete row

if __name__ == '__main__':
    app.run()
