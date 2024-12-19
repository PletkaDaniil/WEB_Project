from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like, Tag, Movie
from . import db
from .recommendation_func import recommend_by_genre,recommend_by_content_rating, recommend_by_author, recommend_by_actor, recommend_by_original_release_year, recommend_by_production_company, recommend_by_plot
import requests
import re

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    posts_sorted_by_likes = sorted(posts, key=lambda post: len(post.likes), reverse=True)
    return render_template("home.html", user=current_user, posts=posts_sorted_by_likes)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        raw_tags = request.form.get('tags')
        tag_names = []
        for tag in raw_tags.split():
            tag = tag.strip().lower()
            if not tag.startswith("#"):
                tag = "#" + tag
            tag_names.append(tag)

        tag_names = set(tag_names)
        if not text:
            flash('Post cannot be empty', category='error')
        elif not raw_tags:
            flash('Tags cannot be empty', category='error')
        else:
            if len(tag_names) > 15:
                flash('You can add up to 15 tags.', category='error')
                return redirect(url_for('views.create_post'))

            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()

            for tag_name in tag_names:
                tag = Tag(name=tag_name, author=current_user.id, post_id=post.id)
                db.session.add(tag)

            db.session.commit()

            flash('Post created with tags!', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        tags = Tag.query.filter_by(post_id=post.id).all()
        for tag in tags:
            db.session.delete(tag)

        comments = Comment.query.filter_by(post_id=post.id).all()
        for comment in comments:
            db.session.delete(comment)

        likes = Like.query.filter_by(post_id=post.id).all()
        for like in likes:
            db.session.delete(like)

        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = sorted(user.posts, key=lambda post: len(post.likes), reverse=True)

    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/tags/<tag_name>")
@login_required
def posts_by_tag(tag_name):
    tag_name = tag_name.strip().lower()
    if not tag_name.startswith("#"):
        tag_name = f"#{tag_name}"

    tags = Tag.query.filter_by(name=tag_name).all()

    if not tags:
        return render_template("tag_posts.html", user=current_user, posts=[], tag_name=tag_name, no_posts=True)

    post_ids = [tag.post_id for tag in tags]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    posts = sorted(posts, key=lambda post: len(post.likes), reverse=True)

    return render_template("tag_posts.html", user=current_user, posts=posts, tag_name=tag_name)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added successfully!', category='success')
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({'error': 'Post does not exist.'}), 400

    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like) 
        db.session.commit()

    db.session.refresh(post)

    return jsonify({
        "likes": len(post.likes),
        "liked": current_user.id in [like.author for like in post.likes]
    })

def fetch_movie_poster(movie_title):
    movie_title = re.sub(r'^\d+\.\s*', '', movie_title)
    movie_title = re.sub(r'\(.*?\)', '', movie_title).strip()
    api_key = current_app.config.get("API_KEY") #your_key
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return data.get("Poster", None)
            else:
                return {"error": data.get("Error")}
        else:
            return {"error": "Failed to connect to OMDb API."}
    except Exception as e:
        return {"error": str(e)}


@views.route("/recommendations-system", methods=['GET', 'POST'])
@login_required
def recommendation_list():
    if request.method == 'POST':
        selected_criterion = request.form.get('criterion')
        user_input = request.form.get('criteria-input')

        if not user_input:
            return jsonify({'error': 'The input cannot be empty'}), 400

        criteria_functions = {
            "1": recommend_by_plot,
            "2": recommend_by_content_rating,
            "3": recommend_by_genre,
            "4": recommend_by_author,
            "5": recommend_by_actor,
            "6": recommend_by_original_release_year,
            "7": recommend_by_production_company
        }

        recommendation_func = criteria_functions.get(selected_criterion)
        if recommendation_func:
            result = recommendation_func(user_input)

            if isinstance(result, dict) and "error" in result:
                return jsonify({'error': result['error']}), 400

            recommendations = result.get("recommendations", [])
            recommendations_with_details = []
            for movie in recommendations:
                if isinstance(movie, str):
                    movie = {'title': str(movie)}

                mov = re.sub(r'^\d+\.\s*', '', movie['title'])                                             
                mov = re.sub(r'\(\d{4}\)$', '', mov).strip()
                movie_data = Movie.query.filter_by(title=mov).first()

                if movie_data:
                    movie['rating'] = movie_data.rating if movie_data.rating else "none"
                    movie['production_company'] = movie_data.production_company if movie_data.production_company else "none"
                    movie['runtime'] = movie_data.runtime if movie_data.runtime else "none"
                    
                    if movie_data.actors:
                        actors = movie_data.actors.split()
                        movie['actors'] = []
                        temp_name = actors[0]
                        for actor in actors[1:]:
                            if actor[0].islower():
                                temp_name += " " + actor
                            else:
                                movie['actors'].append(temp_name)
                                temp_name = actor
                        movie['actors'].append(temp_name)
                        movie['actors'] = [actor.replace('"', '').replace("'", "") for actor in movie['actors'][:6] ] 
                    else:
                        movie['actors'] = ["none", "none", "none", "none", "none", "none"]
                    
                    movie['content_rating'] = movie_data.content_rating if movie_data.content_rating else "none"
                    
                    if movie_data.authors:
                        authors = movie_data.authors.split()
                        movie['authors'] = []
                        temp_name = authors[0]
                        for author in authors[1:]:
                            if author[0].islower():
                                temp_name += " " + author
                            else:
                                movie['authors'].append(temp_name)
                                temp_name = author
                        movie['authors'].append(temp_name)
                        movie['authors'] = [actor.replace('"', '').replace("'", "") for actor in movie['authors'][:6] ] 
                    else:
                        movie['authors'] = ["none", "none", "none", "none"]
                else:
                    movie['rating'] = "none"
                    movie['production_company'] = "none"
                    movie['runtime'] = "none"
                    movie['actors'] = ["none", "none", "none", "none", "none", "none"]
                    movie['content_rating'] = "none"
                    movie['authors'] = ["none", "none", "none", "none"]

                poster_url = fetch_movie_poster(movie['title'])
                movie['poster_url'] = poster_url if isinstance(poster_url, str) else None

                recommendations_with_details.append({
                    "title": movie['title'],
                    "poster_url": movie['poster_url'],
                    "details": {
                        "rating": movie['rating'],
                        "production_company": movie['production_company'],
                        "runtime": movie['runtime'],
                        "actors": movie['actors'],
                        "content_rating": movie['content_rating'],
                        "authors": movie['authors']
                    }
                })

        else:
            recommendations_with_details = [{"title": f"No specific recommendations for '{user_input}'", "poster_url": None}]

        return jsonify({"recommendations": recommendations_with_details})

    return render_template('recommendations_system.html', user=current_user)