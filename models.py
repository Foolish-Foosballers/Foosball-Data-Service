from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db
import enum

class TableSide(enum.Enum):
    LEFT = "Left"
    RIGHT = "Right"

class Player(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    FirstName = db.Column(db.String(120), nullable=False)
    LastName = db.Column(db.String(120), nullable=False)
    Username = db.Column(db.String(9), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    SignupDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    TotalTimePlayed = db.Column(db.Integer, nullable=False, default=0)
    GameWins = db.Column(db.Integer, nullable=False, default=0)
    SeriesWins = db.Column(db.Integer, nullable=False, default=0)
    TotalPoints = db.Column(db.Integer, nullable=False, default=0)
    Shutouts = db.Column(db.Integer, nullable=False, default=0)
    Ranking = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, firstName, lastName, username, email)
        self.FirstName = firstName
        self.LastName = lastName
        self.Username = username
        self.Email = email
        self.SignupDate = datetime.now()
        self.TotalTimePlayed = 0
        self.GameWins = 0
        self.SeriesWins = 0
        self.TotalPoints = 0
        self.Shutouts = 0
        self.Ranking = 0

    def as_dict(self):
        """Method for converting model to a dictionary for JSON serializable output"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Game(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    EndTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    Single = db.Column(db.Boolean, nullable=False)
    LeftScore = db.Column(db.Integer, nullable=False)
    RightScore = db.Column(db.Integer, nullable=False)
    WinMargin = db.Column(db.Integer, nullable=False)
    Winner = db.Column(db.Enum(TableSide), nullable=False)

    def as_dict(self):
        """Method for converting model to a dictionary for JSON serializable output"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Series(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    NumGames = db.Column(db.Integer, nullable=False)
    LeftWins = db.Column(db.Integer, nullable=False)
    RightWins = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        """Method for converting model to a dictionary for JSON serializable output"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class History(db.Model):
    GameId = db.Column(db.Integer, db.ForeignKey('game.Id'), primary_key=True, nullable=False)
    PlayerId = db.Column(db.Integer, db.ForeignKey('player.Id'), primary_key=True, nullable=False)
    SeriesId = db.Column(db.Integer, db.ForeignKey('series.Id'), nullable=False)
    Side = db.Column(db.Enum(TableSide), nullable=False)

    def as_dict(self):
        """Method for converting model to a dictionary for JSON serializable output"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}