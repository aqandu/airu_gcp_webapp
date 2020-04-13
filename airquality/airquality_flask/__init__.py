from dotenv import load_dotenv
import os
from flask import Flask
from google.cloud import bigquery
from google.cloud import datastore
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials, firestore, auth, exceptions
import pyrebase

load_dotenv()       # reference to the .env file that contains account information

config_pyrebase = {
    "apiKey": os.getenv("apiKey"),
    "authDomain": os.getenv("authDomain"),
    "databaseURL": os.getenv("databaseURL"),
    "projectId": os.getenv("projectId"),
    "storageBucket": os.getenv("storageBucket"),
    "messagingSenderId": os.getenv("messagingSenderId"),
    "appId": os.getenv("appId"),
    "measurementId": os.getenv("measurementId")
}

app = Flask(__name__)

# ############################## NEW SETUP ##################################################################
# FIREBASE authentication using PYREBASE wrapper for FIREBASE API
firebase_client = pyrebase.initialize_app(config_pyrebase)
pyrebase_auth = firebase_client.auth()

# FIREBASE authentication handle - not using the PYREBASE wrapper
cred1 = credentials.Certificate(os.getenv("SERVICEACCOUNT"))
default_app = firebase_admin.initialize_app(cred1)
firebase_auth = auth

# BIGQUERY handle / configuration
bq_client = bigquery.Client()

# DATASTORE handle / configuration
ds_client = datastore.Client()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

login_manager = LoginManager(app)

from airquality_flask import routes
