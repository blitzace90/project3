from flask import Flask, render_template, request, redirect, url_for, flash
import pymongo
from dotenv import load_dotenv
from bson import ObjectId
import os
import datetime

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
CLOUD_NAME = os.environ.get('CLOUD_NAME')
UPLOAD_PRESET = os.environ.get('UPLOAD_PRESET')

DB_NAME = "project3_liquor"

SESSION_KEY = os.environ.get('SESSION_KEY')

app.secret_key = SESSION_KEY

# Home Route


@app.route('/')
def home():
    return render_template('home.template.html')

# Read route


@app.route('/liquor/list')
def show_liquor():
    search_liquor = request.args.get('search-liquor')

    criteria = {}
    if search_liquor != "" and search_liquor is not None:
        criteria['name'] = {
            "$regex": search_liquor,
            "$options": "i"
        }

    all_liquor = client[DB_NAME].liquor.find(criteria)

    liquor_type = client[DB_NAME].liquor.find()
    type = request.args.get('type')

    if type and type != 'Type':
        criteria['type'] = type
    else:
        type = 'Type'

    alcohol = client[DB_NAME].liquor.find()
    primary_alcohol = request.args.get('primary_alcohol')

    if primary_alcohol and primary_alcohol != 'Primary Alcohol':
        criteria['primary_alcohol'] = primary_alcohol
    else:
        primary_alcohol = 'Primary Alcohol'

    return render_template('show_liquor.template.html',
                           all_liquor=all_liquor,
                           liquor_type=liquor_type,
                           type=type,
                           alcohol=alcohol,
                           primary_alcohol=primary_alcohol)

# List individual liquor


@app.route("/liquor/list/<id>")
def liquor_details(id):
    liquor = client[DB_NAME].liquor.find_one({
        "_id": ObjectId(id)
    })
    return render_template("liquor_details.template.html",
                           liquor=liquor,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET
                           )

# Add route


@app.route('/liquor/create')
def create_liquor():
    return render_template('create_liquor.template.html',
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET
                           )

# Process add route


@app.route('/liquor/create', methods=["POST"])
def process_create_liquor():
    liquor_name = request.form.get('liquor_name')
    liquor_type = request.form.get('liquor_type')
    primary_alcohol = request.form.get('primary_alcohol')
    serving_method = request.form.get('serving_method')
    standard_drinkware = request.form.get('standard_drinkware')
    ingredients = request.form.get('ingredients')
    preparation = request.form.get('preparation')
    uploaded_file_url = request.form.get('uploaded_file_url')

    client[DB_NAME].liquor.insert_one({
        "name": liquor_name,
        "type": liquor_type,
        "primary_alcohol": primary_alcohol,
        "serving_method": serving_method,
        "standard_drinkware": standard_drinkware,
        "ingredients": ingredients,
        "preparation": preparation,
        "uploaded_file_url": uploaded_file_url
    })
    flash(f"'{liquor_name}' has been added")
    return redirect(url_for('show_liquor'))

# Update route


@app.route('/liquor/update/<id>')
def update_liquor(id):
    liquor = client[DB_NAME].liquor.find_one({
        "_id": ObjectId(id)
    })

    return render_template("update_liquor.template.html",
                           liquor=liquor,
                           cloud_name=CLOUD_NAME,
                           upload_preset=UPLOAD_PRESET
                           )

# Process update route


@app.route('/liquor/update/<id>', methods=["POST"])
def process_update_liquor(id):
    liquor_name = request.form.get('liquor_name')
    liquor_type = request.form.get('liquor_type')
    primary_alcohol = request.form.get('primary_alcohol')
    serving_method = request.form.get('serving_method')
    standard_drinkware = request.form.get('standard_drinkware')
    ingredients = request.form.get('ingredients')
    preparation = request.form.get('preparation')
    uploaded_file_url = request.form.get('uploaded_file_url')

    client[DB_NAME].liquor.update_one({
        "_id": ObjectId(id)
    }, {
        "$set": {
            "name": liquor_name,
            "type": liquor_type,
            "primary_alcohol": primary_alcohol,
            "serving_method": serving_method,
            "standard_drinkware": standard_drinkware,
            "ingredients": ingredients,
            "preparation": preparation,
            "uploaded_file_url": uploaded_file_url
        }
    })
    flash(f"'{liquor_name}' has been updated")
    return redirect(url_for('liquor_details', id=id))

# Delete route


@app.route('/liquor/delete/<id>')
def delete_liquor(id):
    liquor = client[DB_NAME].liquor.find_one({
        "_id": ObjectId(id)
    })

    return render_template('confirm_delete_liquor.template.html',
                           liquor=liquor)

# Process delete route


@app.route('/liquor/delete/<id>', methods=['POST'])
def process_delete_liquor(id):
    client[DB_NAME].liquor.remove({
        "_id": ObjectId(id)
    })
    flash(f"A creation has been deleted")
    return redirect(url_for('show_liquor'))

# Add review route


@app.route('/liquor/list/<id>/review/')
def create_reviews(id):
    liquor = client[DB_NAME].liquor.find_one({
        "_id": ObjectId(id)
    })
    return render_template('create_reviews.template.html', liquor=liquor)

# Process review route


@app.route('/liquor/list/<id>/review/', methods=["POST"])
def process_create_reviews(id):
    username = request.form.get('username')
    date = request.form.get('review-date')
    review = request.form.get('review')

    # convert the string of the data into an actual date object
    date = datetime.datetime.strptime(date, "%Y-%m-%d")

    client[DB_NAME].liquor.update_one({
        "_id": ObjectId(id),
    }, {
        "$push": {
            'reviews': {
                # ObjectId() is a function that returns a new ObjectId
                "_id": ObjectId(),
                "username": username,
                "date": date,
                "review": review
            }
        }
    })

    return redirect(url_for('liquor_details', id=id))

# update review route


@app.route('/review/<review_id>')
def edit_reviews(review_id):
    allReviews = client[DB_NAME].liquor.find_one({
        'reviews._id': ObjectId(review_id)
    }, {
        'reviews': {
            '$elemMatch': {
                '_id': ObjectId(review_id)
            }
        }
    })

    reviews = allReviews['reviews'][0]

    return render_template('edit_reviews.template.html', reviews=reviews)

# process reviews update


@app.route('/review/<review_id>', methods=["POST"])
def process_edit_reviews(review_id):
    liquor = client[DB_NAME].liquor.find_one({
        "reviews._id": ObjectId(review_id)
    })
    id = liquor['_id']
    date = request.form.get('review-date')
    date = datetime.datetime.strptime(date, "%Y-%m-%d")

    client[DB_NAME].liquor.update_one({
        "reviews._id": ObjectId(review_id)
    }, {
        '$set': {
            'reviews.$.username': request.form.get('username'),
            'reviews.$.date': date,
            'reviews.$.review': request.form.get('review')
        }
    })

    return redirect(url_for('liquor_details', id=id))

# delete reviews route


@app.route('/review/<review_id>/delete')
def confirm_delete_review(review_id):
    liquor = client[DB_NAME].liquor.find_one({
        "reviews._id": ObjectId(review_id)
    })
    id = liquor['_id']
    review = client[DB_NAME].liquor.find_one({
        'reviews._id': ObjectId(review_id)
    }, {
        'reviews': {
            '$elemMatch': {
                '_id': ObjectId(review_id)
            }
        }
    })['reviews'][0]

    return render_template('confirm_delete_reviews.template.html',
                           review=review,
                           id=id)

# process delete review


@app.route('/review/<review_id>/delete', methods=["POST"])
def process_delete_review(review_id):
    liquor = client[DB_NAME].liquor.find_one({
        "reviews._id": ObjectId(review_id)
    })
    id = liquor['_id']
    client[DB_NAME].liquor.update_one({
        'reviews._id': ObjectId(review_id)
    }, {
        "$pull": {
            'reviews': {
                '_id': ObjectId(review_id)
            }
        }
    })

    return redirect(url_for('liquor_details', id=id))


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
