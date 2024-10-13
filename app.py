from flask import Flask
from models.db import get_db, get_client
from flask_session import Session 
from views.auth import auth_blueprint
from views.recipes import recipes_blueprint


app = Flask(__name__)
db = get_db()

db.users.create_index("email", unique = True)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['SESSION_TYPE'] = "mongodb"
app.config['SESSION_MONGODB'] = get_client()
Session(app)

# Blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(recipes_blueprint)
