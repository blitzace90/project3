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
    # all_liquor = client[DB_NAME].liquor.find()
    liquor_type = client[DB_NAME].liquor.find()
    search_liquor = request.args.get('search-liquor')
    # print(search_liquor)

    criteria = {}
    if search_liquor != "" and search_liquor is not None:
        criteria['name'] = {
            "$regex": search_liquor,
            "$options": "i"
        }

    all_liquor = client[DB_NAME].liquor.find(criteria)

    return render_template('show_liquor.template.html', all_liquor=all_liquor, liquor_type=liquor_type)

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

    return redirect(url_for('show_liquor'))

# Delete route


@app.route('/liquor/delete/<id>')
def delete_liquor(id):
    liquor = client[DB_NAME].liquor.find_one({
        "_id": ObjectId(id)
    })

    return render_template('confirm_delete_liquor.template.html', liquor=liquor)

# Process delete route


@app.route('/liquor/delete/<id>', methods=['POST'])
def process_delete_liquor(id):
    client[DB_NAME].liquor.remove({
        "_id": ObjectId(id)
    })
    return redirect(url_for('show_liquor'))


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
