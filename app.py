import bcrypt
import os
import hashlib
from flask import Flask, request, redirect, url_for, render_template, make_response, flash, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MongoDB client setup (connecting to MongoDB)
client = MongoClient('mongodb://mongo:27017/')
db = client['flask_auth']  # Database
users_collection = db['users']  # Collection for storing user data
tokens_collection = db['tokens']  # Collection for storing authentication tokens



# Bcrypt setup for password hashing
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Token hashing for security (auth tokens)
def generate_auth_token():
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash

def check_token(token, token_hash):
    return hashlib.sha256(token.encode()).hexdigest() == token_hash

# Route for the home page
# Registration route
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']

    if users_collection.find_one({"username": username}):
        flash('Username already exists.', 'error')
        return redirect(url_for('home'))

    if password1 != password2:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('home'))

    if len(password1) < 12:
        flash('Password must be at least 12 characters long.', 'error')
        return redirect(url_for('home'))

    hashed_password = hash_password(password1)
    users_collection.insert_one({"username": username, "password": hashed_password})

    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('home'))

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = users_collection.find_one({"username": username})

    if user and check_password(user['password'], password):
        token, token_hash = generate_auth_token()
        tokens_collection.insert_one({"username": username, "token_hash": token_hash, "expires_at": datetime.utcnow() + timedelta(hours=1)})

        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('auth_token', token, httponly=True, max_age=60*60)
        resp.set_cookie('username', username)

        flash('Login successful!', 'success')
        return resp
    else:
        flash('Invalid username or password.', 'error')
        return redirect(url_for('home'))

# Route for the home page
@app.route('/')
def home():
    username = request.cookies.get('username')
    return render_template('home.html', username=username)
# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('auth_token', '', expires=0)  # Clear the auth token cookie
    resp.set_cookie('username', '', expires=0)  # Clear the username cookie
    flash('You have been logged out.', 'success')
    return resp


# Middleware to check authentication
def authenticated():
    token = request.cookies.get('auth_token')
    username = request.cookies.get('username')

    if not token or not username:
        return False

    stored_token = tokens_collection.find_one({"username": username})
    if stored_token:
        return check_token(token, stored_token['token_hash']) and datetime.utcnow() < stored_token['expires_at']

    return False

# Ensure that user is authenticated
@app.before_request
def check_authentication():
    if request.path != '/' and request.path != '/login' and request.path != '/register':
        if not authenticated():
            flash('You must be logged in to view this page.')
            return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
