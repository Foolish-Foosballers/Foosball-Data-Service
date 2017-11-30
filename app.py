from flask import Flask
from datetime import datetime
import logging
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class Player(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    FirstName = db.Column(db.String(120), nullable=False)
    LastName = db.Column(db.String(120), nullable=False)
    Username = db.Column(db.String(80), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    SignupDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    TotalTimePlayed = db.Column(db.Integer, nullable=False, default=0)
    GameWins = db.Column(db.Integer, nullable=False, default=0)
    SeriesWins = db.Column(db.Integer, nullable=False, default=0)
    TotalPoints = db.Column(db.Integer, nullable=False, default=0)
    Shutouts = db.Column(db.Integer, nullable=False, default=0)
    Ranking = db.Column(db.Integer, nullable=False, default=0)

class Game(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    EndTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    Single = db.Column(db.Boolean, nullable=False)
    LeftScore = db.Column(db.Integer, nullable=False)
    RightScore = db.Column(db.Integer, nullable=False)
    WinMargin = db.Column(db.Integer, nullable=False)
    Winner = db.Column(db.String(120), nullable=False)

class Series(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    NumGames = db.Column(db.Integer, nullable=False)
    LeftWins = db.Column(db.Integer, nullable=False)
    RightWins = db.Column(db.Integer, nullable=False)

class History(db.Model):
    Id = db.Column(db.String(120), primary_key=True, nullable=False)
    GameId = db.Column(db.Integer, nullable=False)
    PlayerId = db.Column(db.Integer, nullable=False)
    SeriesId = db.Column(db.Integer, nullable=False)
    Side = db.Column(db.String(80), nullable=False)

def createTables():
    app.logger.debug('creating tables')
    db.create_all()
    app.logger.debug('created tables')

@app.route('/')
def homepage():
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug('this will show in the log')
    # db.drop_all()


    # player = Player(Id=0, FirstName="Daniel", LastName="Lerner",
    # Username="dlernz", Email="daniel.lerner@ge.com")
    # db.session.add(player)
    # player = Player(Id=1, FirstName="Sara", LastName="Stik",
    # Username="sarastik", Email="sara.stik@ge.com")
    # db.session.add(player)
    # player = Player(Id=2, FirstName="Brett", LastName="Oberg",
    # Username="wisco", Email="brett.oberg@ge.com")
    # db.session.add(player)
    # db.session.commit()

    # output = Player.query.get(0)
    # app.logger.debug(output.FirstName)
    # output = Player.query.get(1)
    # app.logger.debug(output.FirstName)
    # output = Player.query.get(2)
    # app.logger.debug(output.FirstName)
    
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>

    <img src="http://loremflickr.com/600/400">
    """.format(time=the_time)

if __name__ == '__main__':
    createTables()
    app.run()
