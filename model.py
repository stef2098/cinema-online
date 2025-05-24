from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from datetime import datetime

class Profile(db.Model):
    __tablename__ = "profile" #Kоришћено због проблема препознавања страних кључева
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=100)
    type = db.Column(db.String(10), nullable=False, default="regular")
    tickets = db.relationship("Ticket", backref="profile", cascade='all, delete')

    def __repr__(self):
        return f"Profile {self.id}"
    
class Movie(db.Model):
    __tablename__ = "movie" #Kоришћено због проблема препознавања страних кључева
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False, default="default.jpg")
    description = db.Column(db.String(200), nullable=False)
    genres = db.relationship("MovieGenre", backref="movie", cascade='all, delete')
    projections = db.relationship("Projection", backref="movie", cascade='all, delete')

    def __repr__(self):
        return f"Movie {self.id}"
    
class Genre(db.Model):
    __tablename__ = "genre" #Kоришћено због проблема препознавања страних кључева
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    Moives = db.relationship("MovieGenre", backref="genre")

    def __repr__(self):
        return f"Genre {self.id}"
    
class MovieGenre(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), nullable=False, primary_key=True)

    def __repr__(self):
        return f"MovieGenre {self.movie_id} {self.genre_id}"
    
class CinemaHall(db.Model):
    __tablename__ = "cinemahall" #Kоришћено због проблема препознавања страних кључева
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(10), nullable=False, default="2D")
    projections = db.relationship("Projection", backref="cinemahall")
    seats = db.relationship("Seat", backref="cinemahall")

    def __repr__(self):
        return f"Cinema hall {self.id}"

class Projection(db.Model):
    __tablename__ = "projection" #Kоришћено због проблема препознавања страних кључева
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=600)
    movieid = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    hallid = db.Column(db.Integer, db.ForeignKey("cinemahall.id"), nullable=False)
    tickets = db.relationship("Ticket", backref="projection", cascade='all, delete')
    #movie = db.relationship('Movie', back_populates="projection")

    def __repr__(self):
        return f"Projection {self.id}"
    
class Seat(db.Model):
    __tablename__ = "seat" #Kоришћено због проблема препознавања страних кључева
    id = db.Column(db.Integer, primary_key=True)
    row = db.Column(db.Integer, nullable=False)
    column = db.Column(db.Integer, nullable=False)
    hallid = db.Column(db.Integer, db.ForeignKey("cinemahall.id"), nullable=False)
    tickets = db.relationship("Ticket", backref="seat", cascade='all, delete')

    def __repr__(self):
        return f"Seat {self.row} {self.column}"
    
class Ticket(db.Model):
    __tablename__ = "ticket" #Kоришћено због проблема препознавања страних кључева
    projectionid = db.Column(db.Integer, db.ForeignKey("projection.id"), primary_key=True)
    seatid = db.Column(db.Integer, db.ForeignKey("seat.id"), primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("profile.id"), nullable=True)

    def __repr__(self):
        return f"Ticket {self.projection} {self.seat} {self.user}"

class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(5000), nullable=False)
    image = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"News item {self.id}"