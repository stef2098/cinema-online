from app import app, db
from model import Profile, Movie, Genre, MovieGenre, CinemaHall, Projection, Seat, Ticket
from datetime import datetime

with app.app_context():
    db.create_all()
    p1 = Profile(first_name="Admin", last_name="Admin", email="admin@admin.com", password="12345678", type="admin")
    db.session.add(p1)
    db.session.commit()
