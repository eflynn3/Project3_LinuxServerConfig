#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from .database_setup import Base, Genre, Book, CatalogUser
import random
import string
import json
from flask import make_response
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import requests

CLIENT_ID = ('1020630574838-55nafkeloqlqkemk9riv0pn767pj5n53'
             '.apps.googleusercontent.com')

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


@app.route('/')
def showGenresAndBooks():
    genres = session.query(Genre).all()
    books = session.query(Book).all()
    book_by_id = dict()
    genre_id_to_name = dict()
    for genre in genres:
        genre_id_to_name[genre.id] = genre.name

    # Create dictionary of books
    # map books to their genre's name for simple display
    for book in books:
        try:
            book_by_id[genre_id_to_name[book.genre_id]].append(book)
        except:
            book_by_id[genre_id_to_name[book.genre_id]] = list()
            book_by_id[genre_id_to_name[book.genre_id]].append(book)

    return render_template('main.html', book_dict=book_by_id)


@app.route('/login')
def showLogin():
    # Create state for login
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    data = h.request(url, 'GET')[1]
    result = json.loads(data.decode('utf8'))

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    g_id = credentials.id_token['sub']
    if result['user_id'] != g_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_g_id = login_session.get('g_id')
    if stored_access_token is not None and g_id == stored_g_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['g_id'] = g_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUserID(login_session.get('email'))
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps
                                 ('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]


@app.route('/signout')
def signout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        del login_session['access_token']
        del login_session['g_id']
        del login_session['username']
        del login_session['email']
        del login_session['provider']
        return render_template('successfulSignout.html')
    else:
        return redirect(url_for('showGenresAndBooks'))


@app.route('/books/<int:book_id>')
def getBookById(book_id):
    book = session.query(Book).filter_by(id=book_id).one()
    # Get genre by ID so UI has access to the name
    genre = session.query(Genre).filter_by(id=book.genre_id).one()
    return render_template('bookView.html', book=book.serialize, genre=genre)


@app.route('/books/new', methods=['GET', 'POST'])
def newBook():
    genres = session.query(Genre).all()
    # User cannot create books unless they are logged in
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        genre = session.query(Genre).filter_by(id=request.form['genre']).one()
        newBook = Book(
            title=request.form['title'],
            author=request.form['author'],
            description=request.form['description'],
            genre=genre,
            user_id=login_session['user_id'])
        session.add(newBook)
        session.commit()
        return redirect(url_for('showGenresAndBooks'))
    else:
        return render_template('newBook.html', genres=genres)


@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def editBook(book_id):
    genres = session.query(Genre).all()
    book = session.query(Book).filter_by(id=book_id).one()
    # User id must match the id of the creator, if not they cannot edit
    if 'username' not in login_session:
        return redirect('/login')
    if book.user_id != login_session['user_id']:
        return render_template('alertUser.html', book=book)
    if request.method == 'POST':
        if request.form['title']:
            book.title = request.form['title']
            book.author = request.form['author']
            book.description = request.form['description']
            genre = session.query(
                Genre).filter_by(
                                id=request.form['genre']).one()
            book.genre = genre
        return redirect(url_for('showGenresAndBooks'))
    else:
        return render_template('editBook.html',
                               book=book.serialize, genres=genres)


@app.route('/books/<int:book_id>/delete', methods=['GET', 'POST'])
def deleteBook(book_id):
    book = session.query(
        Book).filter_by(id=book_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    # User id must match the id of the creator, if not they cannot delete
    if book.user_id != login_session['user_id']:
        return render_template('alertUser.html', book=book)

    if request.method == 'POST':
        session.delete(book)
        session.commit()
        return redirect(url_for('showGenresAndBooks', book_id=book_id))
    else:
        return render_template('deleteBook.html', book=book)


@app.route('/genres/new', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGenre = Genre(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newGenre)
        session.commit()
        return redirect(url_for('showGenresAndBooks'))
    else:
        return render_template('newGenre.html')


# Route to see the json for genres
@app.route('/genres/JSON')
def getGenresJson():
    genres = session.query(Genre).all()
    return jsonify(genres=[genre.serialize for genre in genres])


# Route to see the json for books
@app.route('/books/JSON')
def getBooksJson():
    books = session.query(Book).all()
    return jsonify(books=[book.serialize for book in books])

# Route to see the json for arbitrary book
@app.route('/books/<int:book_id>/JSON')
def getArbitraryBookJson(book_id):
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(book=[book.serialize])

# HELPER FUNCTIONS
def createUser(login_session):
    newUser = CatalogUser(name=login_session['username'], email=login_session[
                    'email'])
    session.add(newUser)
    session.commit()
    user = session.query(CatlogUser).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(CatlogUser).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run()
