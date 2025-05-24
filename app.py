from flask import Flask, render_template, url_for, request, session, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from extensions import db
import model as model
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload
from flask_bcrypt import Bcrypt
import threading
import time
import os
from werkzeug.utils  import secure_filename
#Приступ за администратора spavlovic@rg.edu.rs 12345678
#Обичан return искључиво у случајвима када корисник ради недозвољену акцију која захтева заобилажење фронт енда

app = Flask(__name__)
app.secret_key = "kljuc_bioskop"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bioskop.db"
app.config["UPLOAD_EXTENSIONS"] = ["jpg"]
app.config["UPLOAD_DIR"] = "static/images/movies"

db.init_app(app)
bcrypt = Bcrypt(app)

def checkMail(email):
    try:
        user = db.session.execute(db.select(model.Profile).filter_by(email=email)).scalar_one()
        return True
    except:
        return False

def createSession(email):
    session["email"] = email

def getUser():
    if session.get('email'):
        profile=db.session.execute(db.select(model.Profile).filter_by(email=session['email'])).scalar_one()

        return profile
    else: return None

def userid():
    user = getUser()
    if user == None:
        return user
    else:
        return user.id

def isAdmin():
    if session.get('email'):
        profile=db.session.execute(db.select(model.Profile).filter_by(email=session['email'])).scalar_one()

        if profile.type != "admin":
            return False
        return True
    else: return False

def addProjectionToSchedule(hall, movie, actualtime, price):
    projections = model.Projection.query.join(model.Movie).filter(and_(
        actualtime.date() == func.date(model.Projection.time),
        model.Projection.hallid == hall))

    movieObj = model.Movie.query.get(movie)

    #Провера да ли пројекција смета некој пројекцији
    for projection in projections:
        movieDuration = model.Movie.query.get(projection.movieid).duration
        start = projection.time
        end = start + timedelta(minutes=movieDuration)

        start = start.time()
        end = end.time()

        if start <= actualtime.time() <= end or start <= (actualtime + timedelta(minutes=movieObj.duration)).time() <= end:
            return 0
    
    projection = model.Projection(time=actualtime, price=price, movieid=movie, hallid=hall)

    try:
        db.session.add(projection)
        db.session.commit()
        return 1
    except:
        return 0

def deletePassedProjections():
    while True:
        time.sleep(60) 
        with app.app_context():
            now = datetime.now()
            oldProjections = model.Projection.query.filter(model.Projection.time < now).all()
            for projection in oldProjections:
                db.session.delete(projection)
            if oldProjections:
                db.session.commit()

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    movies = model.Movie.query.join(model.Projection).distinct().all()
    news = model.News.query.order_by(model.News.id.desc()).all()

    return render_template("index.html", movielist=movies, news=news)

@app.route("/repertoar/<string:date>")
@app.route("/repertoar")
def repertoar(date=datetime.today().strftime('%d.%m.%Y')):
    date_obj = datetime.strptime(date, '%d.%m.%Y').date()

    movies = model.Movie.query.join(model.Projection).filter(date_obj == func.date(model.Projection.time)).distinct().all()

    for movie in movies:
        movie.filtered_projections = model.Projection.query.filter(
                and_(
                    model.Projection.movieid == movie.id,
                    func.date(model.Projection.time) == date_obj
                )
            ).order_by(model.Projection.time).all()

    return render_template("repertoar.html", movielist=movies, date=date, next_date=(date_obj + timedelta(days=1)).strftime('%d.%m.%Y'), previous_date=(date_obj - timedelta(days=1)).strftime('%d.%m.%Y'))

@app.route("/novosti", methods=["GET", "POST"])
def novosti():
    if request.method == "POST":
        if isAdmin() == False:
            return "Немате адекватне привилегије за ово"

        file = request.files["file"]
        filename = "default.jpg"

        if file.filename != '':
            ext = file.filename.split(".")[-1]
            if (ext not in app.config["UPLOAD_EXTENSIONS"]):
                return "Није дозвољено објављивати овакав формат слике"
            filename = secure_filename(file.filename)
            file_path = os.path.join("static/images/news", filename)
            file.save(file_path)

        title = request.form["title"]
        content = request.form["content"]
        newsItem = model.News(title=title, content=content, image=filename)

        try:
            db.session.add(newsItem)
            db.session.commit()
            return redirect("/nalog")
        except:
            return "Није било могуће креирати вест"
    elif request.method == "GET":
        news = model.News.query.order_by(model.News.id.desc()).all()
        return render_template("novosti.html", news=news)

@app.route("/novosti/<int:id>")
def deleteNews(id):
    if isAdmin() == False:
        return "Немате адекватне привилегије за ово"

    newsitem = model.News.query.get_or_404(id)

    try:
        db.session.delete(newsitem)
        db.session.commit()
        return redirect("/nalog")
    except:
        return "Није било могуће урадити ово"


@app.route("/nalog", methods=["GET", "POST"])
def nalog():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if checkMail(email):
            user = db.session.execute(db.select(model.Profile).filter_by(email=email)).scalar_one()
            is_valid = bcrypt.check_password_hash(user.password, password)
            if is_valid:
                createSession(email)
                return redirect("nalog") 
            else:
                return redirect("nalog") 
        else:
            resp = make_response(redirect("/kreiraj-nalog"))
            resp.set_cookie("email", email)
            resp.set_cookie("password", password)
            return resp
    else:
        profile=None
        movies=[]
        cinemahalls=[]
        projections=[]
        news=[]
        movies = model.Movie.query.all()
        cinemahalls  = model.CinemaHall.query.all()
        tickets = model.Ticket.query.filter_by(userid=userid()).all()
        if session.get('email'):
            profile=db.session.execute(db.select(model.Profile).filter_by(email=session['email'])).scalar_one()
            if profile.type == 'admin':
                projections = model.Projection.query.join(model.Movie).order_by(model.Projection.time).all()
                news = model.News.query.all()
        return render_template("nalog.html", sesija=session, profile=profile, movies=movies, cinemahalls=cinemahalls, projections=projections, news=news, tickets=tickets)

@app.route("/kreiraj-nalog", methods=["GET", "POST"])
def kreirajnalog():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]
        surname = request.form["surname"]
        if checkMail(email):
            return redirect("/nalog")
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') 
            profile = model.Profile(first_name=name, last_name=surname, email=email, password=hashed_password)
            try:
                db.session.add(profile)
                db.session.commit()
                createSession(email)
                return redirect("/nalog")
            except:
                return redirect("/kreiraj-nalog")
    else:
        email = request.cookies.get("email")
        password = request.cookies.get("password")
        resp = make_response(render_template("kreiraj-nalog.html", email=email, password=password))
        resp.set_cookie('email', '', expires=0)
        resp.set_cookie('password', '', expires=0)
        return resp

@app.route("/kupovina/<int:id>")
def kupovina(id):
    projection = model.Projection.query.get_or_404(id)
    movie = model.Movie.query.get(projection.movieid)
    cinemahall = model.CinemaHall.query.get(projection.hallid)
    ticketsL = model.Ticket.query.filter(model.Ticket.projectionid==projection.id).all()
    tickets = {ticket.seatid: ticket for ticket in ticketsL}

    return render_template("kupovina.html", projection=projection, movie=movie, cinemahall=cinemahall, tickets=tickets)

@app.route("/rezervisi/<int:projectionid>/<string:seats>")
def reserveSeats(seats, projectionid):
    if getUser() == None:
        return redirect("/nalog?prijavaPotrebna=true")

    hall = model.CinemaHall.query.join(model.Projection).filter(model.Projection.id==projectionid)[0]
    seatsT = seats.split(',')
    seats = []
    tickets = []
    for i in range(0, len(seatsT) // 2):
        seats.append((seatsT[i * 2], seatsT[i * 2 + 1]))

    for seat in seats:
        seatobj = model.Seat.query.filter(and_(seat[0]==model.Seat.row, seat[1]==model.Seat.column, model.Seat.hallid==hall.id))[0]
        exists = model.Ticket.query.filter(and_(model.Ticket.projectionid==projectionid, model.Ticket.seatid==seatobj.id)).first() is not None
        if exists:
            return "Неко од седишта је већ резервисано"
        ticket = model.Ticket(projectionid=projectionid, seatid=seatobj.id, userid=userid())
        tickets.append(ticket)

    try:
        user = getUser()
        user.points = user.points + 100 * len(seats)
        db.session().add_all(tickets)
        db.session().commit()
    except:
        return "Десила се грешла"
    return redirect("/nalog?kupovina=true")

@app.route("/movie", methods=["POST"])
def addmovie():
    if isAdmin() == False:
        return "Немате адекватне привилегије за ово"
    if (request.method == "POST"):
        title = request.form["title"]
        duration = request.form["duration"]
        description = request.form["description"]

        file = request.files["file"]
        filename = "default.jpg"

        if file.filename != '':
            ext = file.filename.split(".")[-1]
            if (ext not in app.config["UPLOAD_EXTENSIONS"]):
                return "Није дозвољено објављивати овакав формат слике"
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_DIR"], filename)
            file.save(file_path)

        movie = model.Movie(title=title, duration=duration, description=description, image=filename)

        try:
            db.session.add(movie)
            db.session.commit()
            return redirect("/nalog")
        except Exception as e:
            return "Није било могуће додавање у базу"

@app.route("/movie/<int:id>")
def deleteMovie(id):
    if isAdmin() == False:
        return "Немате адекватне привилегије за ово"
    movie = model.Movie.query.get_or_404(id)

    try:
        db.session.delete(movie)
        db.session.commit()
        return redirect("/nalog")
    except:
        return "Није било могуће урадити ово"

@app.route("/schedule", methods=["POST"])
def scheduleMovie():
    if isAdmin() == False:
        return "Немате адекватне привилегије за ово"
    if (request.method == "POST"):
        hall = request.form["hall"]
        movie = request.form["movie"]
        date = request.form["date"]
        time = request.form["time"]
        price = request.form["price"]
        repeat = int(request.form["repeat"])

        datetime_str = f"{date} {time}"
        scheduletime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        added = 0

        for i in range(repeat + 1):
            actualtime = scheduletime + timedelta(days=i)
            added += addProjectionToSchedule(hall, movie, actualtime, price)

        return redirect("/nalog?scheduled="+str(added))

@app.route("/schedule/<int:id>")
def deleteProjection(id):
    if isAdmin() == False:
        return "Немате адекватне привилегије за ово"
    projection = model.Projection.query.get_or_404(id)

    try:
        db.session.delete(projection)
        db.session.commit()
        return redirect("/nalog")
    except:
        return "Није било могуће урадити ово"

@app.route("/log-out")
def logOut():
    session.pop('email', '')
    return redirect("/nalog")

@app.route("/delete-account")
def deleteAccount():
    user = getUser()
    db.session.delete(user)
    db.session.commit()
    return logOut()

@app.route("/edit-account", methods=["GET", "POST"])
def editAccount():
    user = getUser()
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        user.first_name = name
        user.last_name = surname
        user.email = email
        db.session.commit()
        createSession(email)
        return redirect("/nalog")
    else:
        return render_template("edit.html", user=user)


if __name__ == "__main__":
    thread = threading.Thread(target=deletePassedProjections)
    thread.daemon = True
    thread.start()

    app.run(debug=True)