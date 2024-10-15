from flask import flash, redirect, request, url_for
from app import app, db, authenticated

"""
likes collection:
    {   
        "item_id": 1, 
        "likes": [ 
            User1,
            User2,
            ... 
        ]    
    }
"""
likes_collection = db["liked"]

@app.route('/like', methods=['POST'])
def like_post():
    if not authenticated:
        flash('You must be logged in to like this post.')
        return redirect(url_for('itempage'))    # place holder
    
    item_id = 1     # place holder
    username = request.cookie.get('username')
    
    item = likes_collection.find_one({"item_id": item_id})

    if item:
        likes_set = item["likes"]
        if username in likes_set:
            # remove user 
            likes_collection.update_one(
                {"itsem_id": item_id}, 
                {'$pull': {"likes": username}}
            )
        else:
            # add user
            likes_collection.update_one(
                {"item_id": item_id}, 
                {'$addToSet': {"likes": username}}
            )
    else:
        # insert item_id with liked user
        likes_collection.insert_one({
            "item_id": item_id,
            "likes": [username]
        })

    # redirect to current post page with + show the users who liked
    

