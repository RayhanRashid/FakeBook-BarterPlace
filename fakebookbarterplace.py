from flask import Flask, request, redirect, url_for, render_template, make_response, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MongoDB client setup (connecting to the MongoDB container via 'mongo' service name)
client = MongoClient('mongodb://mongo:27017/')
db = client['flask_auth']  # Database
users_collection = db['users']  # Collection for storing user data

# Route for the home page
@app.route('/')
def home():
    username = request.cookies.get('username')
    if username:
        return f'Hello, {username}! You are logged in. <br><a href="/logout">Logout</a>'
    return 'Welcome! <br><a href="/login">Login</a> | <a href="/register">Register</a>'

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists in MongoDB
        if users_collection.find_one({"username": username}):
            flash('Username already exists. Please choose another one.')
        # Enforce strong password: at least 12 characters long
        elif len(password) < 12:
            flash('Password must be at least 12 characters long.')
        else:
            # Hash the password before storing it in the database
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({"username": username, "password": hashed_password})
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

    return render_template('register.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user from the database
        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user['password'], password):
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('username', username)
            return resp
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('username', '', expires=0)  # Clear the cookie
    flash('Logged out successfully.')
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
