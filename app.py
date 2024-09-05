from flask import Flask, render_template, redirect, session
from bson.objectid import ObjectId
from models.db import get_db, get_client
from flask import request
from flask import url_for
from flask import send_from_directory
from flask_session import Session 

from werkzeug.utils import secure_filename
from flask_basicauth import BasicAuth
import os

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
db = get_db()

# App/Flask configuration
app.config['BASIC_AUTH_USERNAME'] = "gojo"
app.config['BASIC_AUTH_PASSWORD'] = "strongest"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = "mongodb"
app.config['SESSION_MONGODB'] = get_client()
Session(app)

# TODO: Proper authentication
basic_auth = BasicAuth(app)

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()
    

# Returns true if filename has an extension in ALLOWED_EXTENSIONS
def allowed_file(filename):
    return ('.' in filename) and \
           get_file_extension(filename) in ALLOWED_EXTENSIONS

# Returns a random filename with the same extension as filename:
def generate_random_filename(filename):
    # If filename is empty, return empty string
    if filename == "":
        return ""
    # Default case
    return str(ObjectId()) + "." + get_file_extension(filename)

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

# Home page
# Lists all recipes and renders `templates/home-page.html`
@app.route("/")
def home_page():
    recipes = db["recipes"]
    result = recipes.find()
    return render_template("home-page.html", recipes=result)


@app.route("/about-us")
def about_us():
    return render_template("about-us.html")

# Gets a single recipe with id <id>
# Gets recipe from db and renders `templates/view-recipe.html` 
@app.route("/recipe/<id>")
def view_recipe(id):
    recipes_collection = db["recipes"]
    recipe = recipes_collection.find_one({"_id": ObjectId(id)})
    return render_template("view-recipe.html", recipe=recipe)

# Form to add recipe
# Renders `templates/create-recipe.html` if GET method
# Adds recipe to db and redirects to /recipe/<id> if POST method 
@app.route("/recipe/create", methods = ["get", "post"])
@basic_auth.required
def create_recipe():
    if request.method == "POST":
        file = request.files['file']
        saved_filename = generate_random_filename(secure_filename(file.filename))
        file_exists = file.filename != ""
        if file_exists and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], saved_filename))
        
        data = request.form
        result = db["recipes"].insert_one({
            "name": data["name"], 
            "type": data["type"], 
            "ingredients": data["ingredients"].split("\n"),
            "image": saved_filename
        })
        return redirect(url_for("view_recipe", id = result.inserted_id))
         
    return render_template("create-recipe.html")

# Delete recipe with id <id>
# Doesn't render any template. Redirects to home page.
@app.route("/recipe/<id>/delete", methods = ["post"] )
@basic_auth.required
def delete_recipe(id):
    db["recipes"].delete_one({"_id": ObjectId(id)})
    return redirect("/")

# Edit existing recipe with id <id>
# Renders form with existing recipe data pre-filled if GET method
# Edits existing recipe with submitted form data if POST method
@app.route("/recipe/<id>/edit", methods = ["get", "post"])
@basic_auth.required
def edit_recipe(id):
    recipe = db["recipes"].find_one({"_id": ObjectId(id)})
    if recipe == None:
        return ("Recipe does not exist.", 404)
    if request.method == "GET":
        return render_template("edit-recipe.html", recipe=recipe)

    # Check if a file was uploaded
    file = request.files['file']
    saved_filename = generate_random_filename(secure_filename(file.filename)) # ""
    file_exists = file.filename != ""
    if file_exists and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], saved_filename))


    data = request.form
    # modified_result is not used for now. It will be when we implement error handling.
    modified_result = db["recipes"].update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "name": data["name"], 
                "type": data["type"], 
                "ingredients": data["ingredients"].split("\n"),
                "image": saved_filename if file_exists else recipe["image"]
            }
        }
    )
    
    return redirect(url_for("view_recipe", id = id))

# #! FOR TESTING
# @app.route('/set/')
# def set():
#     session['user'] = 'gojo satoru'
#     return 'ok'

# @app.route('/get/')
# def get():
#     return session.get('user', 'not set')
 
# @app.route("/register", methods = ["POST", "GET"])
# def register():
#     return render_template("auth/register.html")
