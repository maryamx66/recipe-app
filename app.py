from flask import Flask, send_file, render_template, redirect
from bson.objectid import ObjectId
from models.db import get_db
from flask import request
from flask import url_for
from flask_basicauth import BasicAuth

app = Flask(__name__)
db = get_db()

app.config['BASIC_AUTH_USERNAME'] = "gojo satoru"
app.config['BASIC_AUTH_PASSWORD'] = "special grade"

# TODO: Proper authentication
basic_auth = BasicAuth(app)

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
        data = request.form
        result = db["recipes"].insert_one({
            "name": data["name"], 
            "type": data["type"], 
            "ingredients": data["ingredients"].split("\n")
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


    data = request.form
    # modified_result is not used for now. It will be when we implement error handling.
    modified_result = db["recipes"].update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                 "name": data["name"], 
                "type": data["type"], 
                "ingredients": data["ingredients"].split("\n")
            }
        }
    )
    return redirect(url_for("view_recipe", id = id))

    
    
 