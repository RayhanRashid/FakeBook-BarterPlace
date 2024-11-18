import bcrypt
import os
import hashlib
from flask import Flask, request, redirect, url_for, render_template, make_response, flash, jsonify
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MongoDB client setup (connecting to MongoDB)
client = MongoClient('mongodb://mongo:27017/')
db = client['flask_auth']  # Database
users_collection = db['users']  # Collection for storing user data
tokens_collection = db['tokens']  # Collection for storing authentication tokens
items_collection = db['itmes'] # Collection for storing item posts and likes
bids_colletion = db['bids'] # Collection for storing items and their list of bids
#client.drop_database('flask_auth')

def get_username_from_token():
    auth_token = request.cookies.get('auth_token')
    if not auth_token:
        return None

    # Hash the auth_token to match the stored token_hash
    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()

    # Find the token data based on the hashed token value
    token_data = tokens_collection.find_one({"token_hash": hashed_token})

    # Return the associated username if token data is found
    if token_data:
        return token_data["username"]

    return None

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

# Add 'X-Content-Type-Options: nosniff' header to all responses
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/item', methods=['GET'])
def item():
    item = "item"
    username = get_username_from_token()
    return render_template('itempage/item.html', username = username, item = item)


@app.route('/like', methods=['POST'])
def like_post():
    try:
        item_id = int(request.form['item_id'])
        username = get_username_from_token()
        if not username:
            flash('You must be logged in to like a post.', 'error')
            return redirect(url_for('home'))

        item = items_collection.find_one({"item_id": item_id})

        if item and username not in item['likes']:
            # add user to the likes list and increment the like count
            items_collection.update_one({"item_id": item_id}, {"$push": {"likes": username}, "$inc": {"like_count": 1}})
        elif item and username in item['likes']:
            flash('You have already liked this post.', 'error')
            return redirect(url_for('home'))
        else:
            flash('Post not found.', 'error')
            return redirect(url_for('home'))

        flash('Post liked!', 'success')
        return redirect(url_for('home'))
        
    except Exception as e:
        flash('An error occurred while liking the post.', 'error')
        return redirect(url_for('home'))
    
@app.route('/unlike', methods=['POST'])
def unlike_post():
    try:
        item_id = int(request.form['item_id'])
        username = get_username_from_token()

        if not username:
            flash('You must be logged in to unlike a post.', 'error')
            return redirect(url_for('home'))

        item = items_collection.find_one({"item_id": item_id})

        if item and username in item['likes']:
            # remove user from the likes list and decrement the like count
            items_collection.update_one({"item_id": item_id}, {"$pull": {"likes": username}, "$inc": {"like_count": -1}})
        elif item and username not in item['likes']:
            flash('You have not liked this post.', 'error')
            return redirect(url_for('home'))
        else:
            flash('Post not found.', 'error')
            return redirect(url_for('home'))

        flash('Post unliked!', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash('An error occurred while unliking the post.', 'error')
        return redirect(url_for('home'))

# Route for the home page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            flash('Username already exists.', 'error')
            return redirect(url_for('home'))

        # Check if passwords match
        if password1 != password2:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('home'))

        # Check if password length is at least 12 characters
        if len(password1) < 12:
            flash('Password must be at least 12 characters long.', 'error')
            return redirect(url_for('home'))

        # Hash the password and save the user
        hashed_password = generate_password_hash(password1)
        users_collection.insert_one({"username": username, "password": hashed_password})

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('index.html')  # Render the registration form


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user from the database
        user = users_collection.find_one({"username": username})

        # Verify password and generate token if correct
        if user and check_password_hash(user['password'], password):
            token, token_hash = generate_auth_token()
            token_hash = token_hash
            tokens_collection.insert_one({
                "username": username,
                "token_hash": token_hash,
                "expires_at": datetime.utcnow() + timedelta(hours=1)
            })

            # Set the auth_token cookie
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('auth_token', token, httponly=True, max_age=60*60)

            return resp
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('home'))

    return render_template('index.html')  # Render the login form


# Route for the home page
@app.route('/')
def home():
    print(users_collection)
    print("  ")
    print(tokens_collection)
    items = items_collection.find()
    username = get_username_from_token()
    print(username)

    return render_template('index.html', username=username, items=items)

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    # Get the auth token from cookies
    auth_token = request.cookies.get('auth_token')

    if auth_token:
        # Hash the auth token to match the stored token_hash
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()

        # Remove the token from the database
        tokens_collection.delete_one({"token_hash": hashed_token})

    # Clear the auth token cookie
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('auth_token', '', expires=0)

    flash('You have been logged out.', 'success')
    return resp



# Middleware to check authentication
def authenticated():
    token = request.cookies.get('auth_token')
    username = get_username_from_token()

    if not token or not username:
        return False

    stored_token = tokens_collection.find_one({"username": username})
    if stored_token:
        return check_token(token, stored_token['token_hash']) and datetime.utcnow() < stored_token['expires_at']

    return False

# Ensure that user is authenticated
@app.before_request
def check_authentication():
    if request.path.startswith('/static'):
        return  # Allow static files to load without authentication

    if request.path not in ['/', '/login', '/register','/logout','/post-item', '/post-and-store-item', '/like', '/unlike', '/item']:
        if not authenticated():
            flash('You must be logged in to view this page.')
            return redirect(url_for('home'))


@app.route('/post-item', methods=['GET', 'POST'])
def post_item():
    return render_template('postpage/post.html')

@app.route('/post-and-store-item', methods=['POST'])
def post_and_store_item():
    last_item = items_collection.find_one(sort=[("item_id", -1)])
    if last_item:
        item_id = last_item['item_id'] + 1
    else:
        item_id = 1

    if 'item-image' not in request.files:
        flash('No file found')
        return redirect(url_for('home'))
    
    img_file = request.files['item-image']

    if img_file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))
    
    if img_file and allowed_image_files(img_file.filename):
        filename = secure_filename(img_file.filename)
        item_picture_path = os.path.join('static/images', filename)
        img_file.save(item_picture_path)

    item_name = request.form['item-name']
    item_price = request.form['item-price']
    item_description = request.form['item-description']

    items_collection.insert_one({"item_id": item_id, "item_name": item_name, "item_price": item_price, "item_description": item_description, "item_image": item_picture_path, "likes": [], "like_count": 0})

    return redirect(url_for('home'))


def allowed_image_files(filename):
    allowed_image_file_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    extension_exist = False
    extension_fits = False
    if '.' in filename:
        extension_exist = True

    if filename.rsplit('.',1)[1].lower() in allowed_image_file_extensions:
        extension_fits = True

    if extension_exist and extension_fits:
        return True
    else:
        return False


        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
