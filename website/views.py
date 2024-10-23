from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db


views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
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

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


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
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})


@views.route("/recommendations-system", methods=['GET', 'POST'])
@login_required
def recommendation_list():
    if request.method == 'POST':
        # Получаем выбранный критерий и введённый текст из формы
        selected_criterion = request.form.get('criterion')  # Получаем выбранный пункт
        user_input = request.form.get('criteria-input')  # Получаем введённый текст

        if not user_input:
            return jsonify({'error': 'The input cannot be empty'}), 400

        recommendations = []
        if selected_criterion == "1":  
            recommendations = [f'Recommended movie based on plot "{user_input}"']
        elif selected_criterion == "2":  
            recommendations = [f'Movies with content rating "{user_input}"']
        elif selected_criterion == "3": 
            recommendations = ['hello', 'hellohellohellohello', 'hello','hello', 'hellohellohellohello', 'hellohellohellohellohellohello','hello', 'hello', 'hello','hello', 'hello', 'hello']  # Возвращаем тестовые данные
        elif selected_criterion == "4": 
            recommendations = [f'Movies by author "{user_input}"']
        elif selected_criterion == "5":  
            recommendations = [f'Movies featuring actor "{user_input}"']
        elif selected_criterion == "6":  
            recommendations = [f'Movies from release year "{user_input}"']
        elif selected_criterion == "7":  
            recommendations = [f'Movies with runtime of "{user_input}" minutes']
        elif selected_criterion == "8":
            recommendations = [f'Movies from production company "{user_input}"']
        else:
            recommendations = [f'No specific recommendations for "{user_input}"']
        return jsonify({"recommendations": recommendations})

    return render_template('recommendations_system.html', user=current_user)
