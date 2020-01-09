from dotenv import load_dotenv
import os
from flask import Flask
from google.cloud import bigquery
from flask_login import LoginManager

import firebase_admin
from firebase_admin import credentials, firestore, auth, exceptions

import pyrebase

load_dotenv()

# This configuration is used for Firebase connection
config = {
    "apiKey": os.getenv("APIKEY"),
    "authDomain": os.getenv("AUTHDOMAIN"),
    "databaseURL": os.getenv("DATABASEURL"),
    "storageBucket": os.getenv("STORAGEBUCKET"),
    "serviceAccount": os.getenv("SERVICEACCOUNT"),
}

app = Flask(__name__)

# Credential for FIREBASE (using the database to store user information and authentication for username/password)
cred = credentials.Certificate(os.getenv("SERVICEACCOUNT"))
fire_app = firebase_admin.initialize_app(cred)

firestore_client = firestore.client()       # used for a db handle
firestore_auth = auth                       # used for authentication
# USING FIREBASE API

# USING PYREBASE4 - WRAPPER FOR FIREBASE API
fire = pyrebase.initialize_app(config)
pyrebase_auth = fire.auth()

bq_client = bigquery.Client()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

login_manager = LoginManager(app)

from airu_flask import routes