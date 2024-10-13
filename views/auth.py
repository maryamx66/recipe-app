from bcrypt import hashpw, gensalt, checkpw
from flask import Blueprint, flash, redirect, render_template, request, session
from pymongo.errors import DuplicateKeyError
from models.db import db
import re

auth_blueprint = Blueprint("auth_blueprint" ,__name__, template_folder= "templates")


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

def is_logged_in():
    if session.get("user", None):
        return True
    else:
        return False
 
@auth_blueprint.route("/auth/register", methods = ["POST", "GET"])
def register():
    if is_logged_in():
        return redirect("/")
    # POST method handling
    if request.method == "POST":
        submitted_data = request.form
        try:
            if not EMAIL_REGEX.match(submitted_data["email"]):
                return render_template("auth/register.html", error = "Email is not valid!")
            if len(submitted_data["password"]) < 8:
                return render_template("auth/register.html", error = "Password must be no less than 8 characters!")
            user_data = db["users"].insert_one({
                "email": submitted_data["email"],
                "password": hashpw(password=str(submitted_data["password"]).encode(), salt=gensalt()),
            })
            
            session["user"] = str(user_data.inserted_id)
            flash("You were registered successfully!")
            return redirect("/")
        except DuplicateKeyError:
            return render_template("auth/register.html", error = "Email is already taken!")
            
    # GET Method handling
    else:
        return render_template("auth/register.html")
    
@auth_blueprint.route("/auth/login", methods = ["POST", "GET"])
def login(): 
    if is_logged_in():
        return redirect("/")
    if request.method == "POST":
        submitted_data = request.form
        
        user_data = db["users"].find_one(
            {"email": submitted_data["email"]}
        )

        # If user doesn't exist (email incorrect) OR password is incorrect
        if user_data == None or not checkpw(str(submitted_data["password"]).encode(), user_data["password"]):
            return render_template("auth/login.html", error = "Email or password is incorrect!")
        
        session["user"] = str(user_data["_id"])
        flash("Welcome back!")
        return redirect("/")
    else:
        return render_template("auth/login.html")


@auth_blueprint.route("/auth/logout")
def logout():
    session.clear()
    return redirect("/")