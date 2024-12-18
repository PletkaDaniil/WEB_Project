import pytest
from website import create_app, db
from website.models import User, Movie, Post, Comment
from website.views import fetch_movie_poster


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def temp_user(app):
    with app.app_context():
        user = User(username="tempuser", email="temp@example.com", password="temppassword")
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()

def test_user_creation(app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com", password="testpassword")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert User.query.count() >= 1

def test_homepage(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)

    response = client.get('/')
    assert response.status_code == 200 
    print("Главная страница доступна для авторизованного пользователя.")

def test_login_page(client):
    response = client.get('/login') 
    assert response.status_code == 200 

def test_load_movies_from_csv(app):
    from website import load_movies_from_csv
    test_csv = 'rotten_tomatoes_ratings.csv'

    with app.app_context():
        load_movies_from_csv(test_csv)

        movie_count = Movie.query.count()
        assert movie_count > 0

def test_sign_up_page(client):
    response = client.get('/sign-up')
    assert response.status_code == 200

def test_sign_up_invalid_data_1(client):
    response = client.post('/sign-up', data={
        'email': 'invalid-email',
        'username': 'testuser',
        'password1': 'short',
        'password2': 'short'
    })
    assert response.status_code == 200
    assert b"Password is too short." in response.data

def test_sign_up_invalid_data_2(client):
    response = client.post('/sign-up', data={
        'email': 'invalid-email',
        'username': 'testuser',
        'password1': 'shortshort',
        'password2': 'shortshort'
    })
    assert response.status_code == 200
    assert b"Invalid email address. Please enter a valid email." in response.data

def test_sign_up_invalid_data_3(client):
    response = client.post('/sign-up', data={
        'email': 'invalid-email',
        'username': 'testuser',
        'password1': 'shortshort',
        'password2': 'shortshortt'
    })
    assert response.status_code == 200
    assert b"Passwords don&#39;t match." in response.data

def test_sign_up_invalid_data_4(client):
    response = client.post('/sign-up', data={
        'email': 'invalid-email',
        'username': 'hi',
        'password1': 'shortshort',
        'password2': 'shortshort'
    })
    assert response.status_code == 200
    assert b"Username is too short." in response.data

def test_logout(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)
    
    response = client.get('/logout')
    assert response.status_code == 302
    assert b'/home' in response.data

def test_create_post_success(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)
    
    response = client.post('/create-post', data={
        'text': 'This is a test post.',
        'tags': '#test #post'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Post created with tags!" in response.data


def test_create_post_no_text(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)
    
    response = client.post('/create-post', data={
        'text': '',
        'tags': '#test #post'
    })
    assert response.status_code == 200
    assert b'Post cannot be empty' in response.data

def test_create_post_no_tags(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)
    
    response = client.post('/create-post', data={
        'text': 'This is a test post.',
        'tags': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Tags cannot be empty' in response.data

def test_create_post_excessive_tags(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)

    response = client.post('/create-post', data={
        'text': 'Post with too many tags',
        'tags': ' '.join(f'#{i}' for i in range(20))
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'You can add up to 15 tags.' in response.data


def test_delete_post_success(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)

    response = client.post('/create-post', data={
        'text': 'Post to be deleted',
        'tags': '#delete #post'
    }, follow_redirects=True)
    assert response.status_code == 200

    post_id = Post.query.filter_by(text='Post to be deleted').first().id

    response = client.get(f'/delete-post/{post_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Post deleted.' in response.data

def test_create_comment_success(client, temp_user, app):
    with app.app_context():
        post = Post(text="Post for comment", author=temp_user.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)

    response = client.post(f'/create-comment/{post_id}', data={'text': 'This is a comment'}, follow_redirects=True)

    assert response.status_code == 200
    assert b'Comment added successfully!' in response.data
    with app.app_context():
        comment = Comment.query.filter_by(post_id=post_id, text='This is a comment').first()
        assert comment is not None


def test_delete_comment_not_found(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)

    response = client.get('/delete-comment/9999', follow_redirects=True)
    assert response.status_code == 200
    assert b'Comment does not exist.' in response.data


def test_delete_comment_no_permission(client, temp_user, app):
    with app.app_context():
        another_user = User(username="anotheruser", email="another@example.com", password="password")
        db.session.add(another_user)
        db.session.commit()

        post = Post(text="Post for comment", author=another_user.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
        comment = Comment(text="This is a comment", author=another_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)

    response = client.get(f'/delete-comment/{comment_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'You do not have permission to delete this comment.' in response.data


def test_like_post(client, temp_user, app):
    with app.app_context():
        post = Post(text="Post to like", author=temp_user.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)

    response = client.post(f'/like-post/{post_id}')

    assert response.status_code == 200

    with app.app_context():
        post = Post.query.get(post_id)
        db.session.refresh(post)
        assert post is not None
        assert len(post.likes) == 1

    with client.session_transaction() as session:
        json_data = response.get_json()
        assert 'likes' in json_data
        assert json_data['likes'] == 1
        assert json_data['liked'] is True

    response = client.post(f'/like-post/{post_id}')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['likes'] == 0
    assert json_data['liked'] is False


def test_fetch_movie_poster_success(app):
    movie_title = "Inception"
    with app.app_context():
        poster_url = fetch_movie_poster(movie_title)
        assert isinstance(poster_url, str)
        assert poster_url.startswith("http")


def test_fetch_movie_poster_invalid_movie(app):
    movie_title = "NonexistentMovie12345"
    with app.app_context():
        result = fetch_movie_poster(movie_title)
        assert isinstance(result, dict)
        assert 'error' in result


def test_recommendations_success(client, temp_user):
    with client.session_transaction() as session:
        session['_user_id'] = str(temp_user.id)

    response = client.post('/recommendations-system', data={
        'criterion': '3',
        'criteria-input': 'Action'
    })
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'recommendations' in json_data
    assert isinstance(json_data['recommendations'], list)