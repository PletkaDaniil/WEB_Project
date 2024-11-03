from .models import Movie
from sqlalchemy import desc, func
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_by_plot(movie_title):
    movie_title = movie_title.strip().lower()

    target_movie = Movie.query.filter(
        func.lower(Movie.title) == movie_title,
        Movie.info.isnot(None), Movie.info != '', Movie.info != '0'
    ).first()
    
    if not target_movie:
        return {"error": "Movie not found or has no plot information. Please enter a valid movie title."}
    
    target_plot = target_movie.info.lower()

    movies = Movie.query.filter(
        Movie.info.isnot(None), Movie.info != '', Movie.info != '0',
        Movie.original_release_date >= 1990,
        Movie.rating >= 5,
        Movie.id != target_movie.id
    ).all()

    movie_plots = [target_plot] + [movie.info.lower() for movie in movies]
    
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(movie_plots)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    movie_similarities = [(movie, similarity) for movie, similarity in zip(movies, cosine_similarities) if similarity > 0.1]
    
    movie_similarities = sorted(movie_similarities, key=lambda x: (x[1], x[0].rating), reverse=True)

    recommendations = []
    counter = 1
    for movie, similarity in movie_similarities:
        recommendations.append(f"{counter}. {movie.title} ({int(movie.original_release_date)})")
        counter += 1

    return {"recommendations": recommendations}


def recommend_by_content_rating(content_rating):
    content_rating = content_rating.strip().lower()
    valid_ratings = {'g', 'pg', 'pg-13', 'nr', 'r'}
    
    if content_rating not in valid_ratings:
        return {"error": "Invalid content rating. Please enter one of the following: G, PG, PG-13, NR, R"}
    
    year_ranges = [(2015, 2020), (2010, 2015), (2005, 2010), (2000, 2005), (1995, 2000), (1990, 1995)]
    recommendations = []
    counter = 1

    for start_year, end_year in year_ranges:
        movies = Movie.query.filter(
            func.lower(Movie.content_rating) == content_rating,
            Movie.original_release_date >= start_year,
            Movie.original_release_date < end_year,
            Movie.info.isnot(None), Movie.info != '', Movie.info != '0',
            Movie.critics_consensus.isnot(None), Movie.critics_consensus != '', Movie.critics_consensus != '0',
            Movie.original_release_date.isnot(None), Movie.original_release_date != '', Movie.original_release_date != 0,
        ).order_by(desc(Movie.rating)).limit(20).all()

        for movie in movies:
            recommendations.append(f"{counter}. {movie.title} ({int(movie.original_release_date)})")
            counter += 1
    
    return {"recommendations": recommendations}


def recommend_by_genre(genre):
    genre = genre.lower().strip()
    
    year_ranges = [(2015, 2020), (2010, 2015), (2005, 2010), (2000, 2005), (1995, 2000), (1990, 1995)]
    recommendations = []
    counter = 1

    for start_year, end_year in year_ranges:
        movies = Movie.query.filter(
            func.lower(Movie.genres).like(f"%{genre}%"),
            Movie.original_release_date >= start_year,
            Movie.original_release_date < end_year,
            Movie.info.isnot(None), Movie.info != '', Movie.info != '0',
            Movie.critics_consensus.isnot(None), Movie.critics_consensus != '', Movie.critics_consensus != '0',
            Movie.original_release_date.isnot(None), Movie.original_release_date != '', Movie.original_release_date != 0,
        ).order_by(desc(Movie.rating)).limit(20).all()

        for movie in movies:
            recommendations.append(f"{counter}. {movie.title} ({int(movie.original_release_date)})")
            counter += 1
    
    return {"recommendations": recommendations}


def recommend_by_author(author_name):
    author_name = author_name.lower().strip()

    movies = Movie.query.filter(
        func.lower(Movie.authors).like(f"%{author_name}%"),
        Movie.info.isnot(None), Movie.info != '', Movie.info != '0',
        Movie.critics_consensus.isnot(None), Movie.critics_consensus != '', Movie.critics_consensus != '0',
        Movie.original_release_date.isnot(None), Movie.original_release_date != '', Movie.original_release_date != 0,
    ).order_by(desc(Movie.rating)).all()

    recommendations = []
    counter = 1

    for movie in movies:
        recommendations.append(f"{counter}. {movie.title} ({int(movie.original_release_date)})")
        counter += 1
    
    return {"recommendations": recommendations}


def recommend_by_actor(actor_name):
    actor_name = actor_name.lower().strip()  

    movies = Movie.query.filter(
        func.lower(Movie.actors).like(f"%{actor_name}%"),
        Movie.info.isnot(None), Movie.info != '', Movie.info != '0',
        Movie.critics_consensus.isnot(None), Movie.critics_consensus != '', Movie.critics_consensus != '0',
        Movie.original_release_date.isnot(None), Movie.original_release_date != '', Movie.original_release_date != 0,
    ).order_by(desc(Movie.rating)).all()

    recommendations = []
    counter = 1

    for movie in movies:
        recommendations.append(f"{counter}. {movie.title} ({int(movie.original_release_date)})")
        counter += 1
    
    return {"recommendations": recommendations}


def recommend_by_original_release_year(year):
    try:
        year = int(year)
    except ValueError:
        return {"error": "Invalid year format. Please enter a valid year."}

    movies = Movie.query.filter(
        Movie.original_release_date == year,
        Movie.info.isnot(None), Movie.info != '', Movie.info != '0',
        Movie.critics_consensus.isnot(None), Movie.critics_consensus != '', Movie.critics_consensus != '0',
        Movie.original_release_date.isnot(None), Movie.original_release_date != '', Movie.original_release_date != 0,
    ).order_by(desc(Movie.rating)).all()

    recommendations = []
    counter = 1

    for movie in movies:
        recommendations.append(f"{counter}. {movie.title} ({int(movie.original_release_date)})")
        counter += 1
    
    return {"recommendations": recommendations}

def recommend_by_production_company(company_name):
    company_name = company_name.strip().lower()
    
    year_ranges = [(2015, 2020), (2010, 2015), (2005, 2010), (2000, 2005), (1995, 2000), (1990, 1995)]
    recommendations = []
    counter = 1

    for start_year, end_year in year_ranges:
        movies = Movie.query.filter(
            func.lower(Movie.production_company).like(f"%{company_name}%"),
            Movie.original_release_date >= start_year,
            Movie.original_release_date < end_year,
            Movie.info.isnot(None), Movie.info != '', Movie.info != '0',
            Movie.critics_consensus.isnot(None), Movie.critics_consensus != '', Movie.critics_consensus != '0',
            Movie.original_release_date.isnot(None), Movie.original_release_date != '', Movie.original_release_date != 0,
        ).order_by(desc(Movie.rating)).all()

        for movie in movies:
            recommendations.append(f"{counter}. {movie.title} ({int(movie.original_release_date)})")
            counter += 1
    
    return {"recommendations": recommendations}