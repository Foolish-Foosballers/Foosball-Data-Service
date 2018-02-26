from flask import Flask, abort, request, jsonify
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os, json, logging
import playerRankings as rank

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
        <li><a href="/history">/history</a></li>
        <li><a href="/rankings">/rankings</a></li>
        <li><a href="/leaderboard">/leaderboard</a></li>
    </ul>
    """

@app.route('/players', methods=['GET'])
def getPlayers():
    players = Players.query.all()
    return json.dumps([player.as_dict() for player in players], default=jsonSerial)

# @app.route('/players/<int:id>', methods=['GET'])
# def getPlayerById(id):
#     player = Players.query.get_or_404(id)
#     return json.dumps(player.as_dict(), default=jsonSerial)

@app.route('/players/<int:username>', methods=['GET'])
def getPlayerByUsername(username):
    player = Players.query.filter_by(Username=username).first_or_404()
    return json.dumps(player.as_dict(), default=jsonSerial)

@app.route('/games', methods=['GET'])
def getGames():
    app.logger.debug("getting games")
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

@app.route('/rankings', methods=['GET'])
def getRankings():
    sortedPlayers = Players.query.filter(Players.Ranking != 0).order_by(Players.Ranking).all()
    return json.dumps([player.as_dict() for player in sortedPlayers], default=jsonSerial)

@app.route('/leaderboard', methods=['GET'])
def getLeaderboard():
    leaderboard = []
    sortedPlayers = Players.query.filter(Players.Ranking != 0).order_by(Players.Ranking).all()
    for player in sortedPlayers:
        row = {}
        row["First Name"] = player.FirstName
        row["Last Name"] = player.LastName
        row["Ranking"] = player.Ranking
        row["Series Wins"] = player.SeriesWins
        row["Game Wins"] = player.GameWins
        row["Game Losses"] = player.TotalGamesPlayed - player.GameWins
        row["Points Scored"] = player.TotalPoints
        row["Shutouts"] = player.Shutouts 
        row["Game Win %"] = round(100.0*player.GameWins / player.TotalGamesPlayed,2)
        numSeriesPlayed = db.session.query(func.distinct(Series.Id)).join(History).filter(History.PlayerId == player.Id).count()
        row["Series Win %"] = round(100.0*player.SeriesWins / numSeriesPlayed,2)
        row["Avg Points/Game"] = round(player.TotalPoints / player.TotalGamesPlayed,2)
        sumWinMargin = db.session.query(func.sum(Games.WinMargin)).join(History).filter(Games.Winner == History.Side).filter(History.PlayerId == player.Id).scalar()
        row["Avg Win Margin"] = round(sumWinMargin / player.TotalGamesPlayed,2)
        leaderboard.append(row)
    return json.dumps(leaderboard)

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
    
    newGame = Games(request.json['Duration'],
                    request.json['Single'],
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
# PUT
####################
@app.route('/players/<int:id>', methods=["PUT"])
def updatePlayer(id):
    if not request.json:
        abort(400)
    db.session.query(Players).filter_by(Id = id).update(request.json)
    db.session.commit()
    app.logger.debug(request.json)
    return (jsonify(request.json), 202)

@app.route('/updateRankings', methods=['PUT'])
def updateRankings():
    games = Games.query.all()
    matchupsSeen = set()
    gameTups = []
    for game in games:
        gameHistory = History.query.filter_by(GameId = game.Id)
        gameHists = [game.as_dict() for game in gameHistory]

        # If pair of players has not been seen, find num of games each pair has played with each other
        if (gameHists[0]["PlayerId"], gameHists[1]["PlayerId"]) not in matchupsSeen:
            if len(gameHists) == 2:
                commonGames = []
                player1 = Players.query.filter_by(Id = gameHists[0]["PlayerId"]).first()
                player2 = Players.query.filter_by(Id = gameHists[1]["PlayerId"]).first()
                play1Games = History.query.filter_by(PlayerId = player1.Id)
                play1Games = [game.as_dict() for game in play1Games]
                play2Games = History.query.filter_by(PlayerId = player2.Id)
                play2Games = [game.as_dict() for game in play2Games]
                play2GamesById = {}
                for game in play2Games:
                    _id = game["GameId"]
                    play2GamesById[_id] = game
                for game in play1Games:
                    _id = game["GameId"]
                    if _id in play2GamesById:
                        commonGames.append(game)

                # create two entries mapping (player1, player2, numTimesPlayed, player1Wins, player1Loss)
                p1Entry = (player1.Id, player2.Id, len(commonGames), player1.GameWins, len(play1Games) - player1.GameWins)
                p2Entry = (player2.Id, player1.Id, len(commonGames), player2.GameWins, len(play2Games) - player2.GameWins)
                gameTups.append(p1Entry)
                gameTups.append(p2Entry)
                matchupsSeen.add((player1.Id, player2.Id))
                matchupsSeen.add((player2.Id, player1.Id))

    # Get new rankings based on game data, sort ids based on ranking, and update player rankings
    rankings = rank.updateRankings(gameTups)
    sortedRanks = sorted([(value,key) for (key,value) in rankings.items()], reverse=True)
    allPlayers = Players.query.all()
    allPlayersDict = {}
    for player in allPlayers: 
        allPlayersDict[player.Id] = player
    for i in range(len(sortedRanks)):
        _id = sortedRanks[i][1]
        player = allPlayersDict[_id]
        player.Ranking = i + 1    
    db.session.commit()
    return (json.dumps([player.as_dict() for player in allPlayers], default=jsonSerial), 202)

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
