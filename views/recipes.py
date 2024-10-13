import os
from bson import ObjectId
from flask import flash, redirect, render_template, request, send_from_directory, session, url_for, Blueprint, current_app
from werkzeug.utils import secure_filename
from models import db
from models.db import db

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

recipes_blueprint = Blueprint("recipes_blueprint", __name__, template_folder= "templates")


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

@recipes_blueprint.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)

# Home page
# Lists all recipes and renders `templates/home-page.html`
@recipes_blueprint.route("/")
def home_page():
    recipes = db["recipes"]
    result = recipes.find()
    return render_template("home-page.html", recipes=result)


@recipes_blueprint.route("/about-us")
def about_us():
    return render_template("about-us.html")

# Gets a single recipe with id <id>
# Gets recipe from db and renders `templates/view-recipe.html` 
@recipes_blueprint.route("/recipe/<id>")
def view_recipe(id):
    recipes_collection = db["recipes"]
    recipe = recipes_collection.find_one({"_id": ObjectId(id)})
    return render_template("view-recipe.html", recipe=recipe)

# Form to add recipe
# Renders `templates/create-recipe.html` if GET method
# Adds recipe to db and redirects to /recipe/<id> if POST method 
@recipes_blueprint.route("/recipe/create", methods = ["get", "post"])
def create_recipe():
    current_user_id = session.get("user", None)
    if current_user_id == None:
        flash("You must be logged in to create a recipe!")
        return redirect("/auth/login")
    
    if request.method == "POST":
        file = request.files['file']
        saved_filename = generate_random_filename(secure_filename(file.filename))
        file_exists = file.filename != ""
        if file_exists and allowed_file(file.filename):
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], saved_filename))
        

        data = request.form
        result = db["recipes"].insert_one({
            "user_id": current_user_id,
            "name": data["name"], 
            "type": data["type"], 
            "ingredients": data["ingredients"].split("\n"),
            "image": saved_filename
        })
        return redirect(url_for("recipes_blueprint.view_recipe", id = result.inserted_id))
         
    return render_template("create-recipe.html")

# Delete recipe with id <id>
# Doesn't render any template. Redirects to home page.
@recipes_blueprint.route("/recipe/<id>/delete", methods = ["post"] )
def delete_recipe(id):
    current_user_id = session.get("user", None)

    if current_user_id == None:
        flash("You must be logged in to edit a recipe!")
        return redirect("/auth/login")
    
    recipe = db["recipes"].find_one({"_id": ObjectId(id)})
    if current_user_id != recipe["user_id"]:
        flash("You cannot delete this recipe!")
        return redirect(f"/recipe/{id}")

    db["recipes"].delete_one({"_id": ObjectId(id)})
    return redirect("/")

# Edit existing recipe with id <id>
# Renders form with existing recipe data pre-filled if GET method
# Edits existing recipe with submitted form data if POST method
@recipes_blueprint.route("/recipe/<id>/edit", methods = ["get", "post"])
def edit_recipe(id):
    current_user_id = session.get("user", None)
    if current_user_id == None:
        flash("You must be logged in to edit a recipe!")
        return redirect("/auth/login")
    
    recipe = db["recipes"].find_one({"_id": ObjectId(id)})
    if recipe == None:
        return ("Recipe does not exist.", 404)
    if current_user_id != recipe["user_id"]:
        flash("You cannot edit this recipe!")
        return redirect(f"/recipe/{id}")
    if request.method == "GET":
        return render_template("edit-recipe.html", recipe=recipe)

    # Check if a file was uploaded
    file = request.files['file']
    saved_filename = generate_random_filename(secure_filename(file.filename)) # ""
    file_exists = file.filename != ""
    if file_exists and allowed_file(file.filename):
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], saved_filename))


    data = request.form
    db["recipes"].update_one(
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