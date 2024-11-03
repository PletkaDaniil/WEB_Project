from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
import pandas as pd

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "hello_world"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    @app.after_request
    def log_request(response):
        if current_user.is_authenticated:
            log_entry = Log(
                action=f"{request.method} {request.path}",
                user_id=current_user.id,
                details=f"Status code: {response.status_code}, IP: {request.remote_addr}"
            )
            db.session.add(log_entry)
            db.session.commit()
        return response

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Post, Comment, Like, Movie, Log

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    with app.app_context():
        if Movie.query.count() == 0:
            load_movies_from_csv('rotten_tomatoes_ratings.csv')

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()


def load_movies_from_csv(csv_file):
    from .models import Movie

    df = pd.read_csv(csv_file, delimiter=',')

    movies_data = []

    for index, row in df.iterrows():
        release_year = int(row['original_release_date']) if not pd.isnull(row['original_release_date']) else None

        movie_data = {
            "title": row['movie_title'],
            "info": row['movie_info'],
            "critics_consensus": row['critics_consensus'],
            "content_rating": row['content_rating'],
            "genres": row['genres'],
            "authors": row['authors'],
            "actors": row['actors'],
            "original_release_date": release_year,
            "runtime": int(row['runtime']) if not pd.isnull(row['runtime']) else None,
            "production_company": row['production_company'],
            "rating": float(row['rating'])
        }

        movies_data.append(movie_data)

    db.session.bulk_insert_mappings(Movie, movies_data)
    db.session.commit()