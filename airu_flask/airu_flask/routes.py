from dotenv import load_dotenv
import os
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_mail import Mail, Message
from airu_flask.forms import RegistrationForm, LoginForm, ForgotPasswordForm
from airu_flask import app, bq_client, firestore_client, firestore_auth, pyrebase_auth
from airu_flask.models import User
from flask_login import login_user, current_user, logout_user
import json

load_dotenv()

projectId = os.getenv("PROJECTID")
datasetId = os.getenv("DATASETID")
tableId = os.getenv("TABLEID")
sensor_table = os.getenv("BIGQ_SENSOR")
# tableRef = bq_client.dataset(datasetId).table(tableId)
# table = bq_client.get_table(tableRef)

app.config.update(
    DEBUG=True,
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=os.getenv("MAIL_PORT"),
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
)

mail = Mail(app)

@app.route('/')
def home():
    return render_template("home.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create FIREBASE AUTHENTICATION CREDENTIALS
        firestore_auth.create_user(
            email=form.email.data,
            password=form.password.data)

        # generate a link to validate email address - this is an added security measure
        # this link will be sent to the user in the auto generated email
        # if the user fails to validate the email address then we will deny login access
        email_link = firestore_auth.generate_email_verification_link(form.email.data)

        # store user data in the "users" collection - document name is the user's email address
        doc_ref = firestore_client.collection('users').document(form.email.data)
        doc_ref.set({
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'street_address': form.street_address.data,
            'city_address': form.city.data,
            'state_address': form.state.data,
            'zip_code': form.zip_code.data,
            'email': form.email.data,
            'admin': False
        })

        flash(f'Registration complete for {form.email.data}!', 'flash_success')
        # Send email to admin and user
        rtnCode = send_registration_email(form, email_link)
        if rtnCode=="sent":
            flash(f'An email confirmation has been sent.', 'flash_success')
        else:
            return render_template("error.html", title="Error", error=rtnCode)
        return redirect(url_for('home'))
    # Form NOT validated
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        valid_user = User(form.email.data)
        try:
            user = pyrebase_auth.sign_in_with_email_and_password(form.email.data, form.password.data)
        except:
            flash(f'Incorrect password for: {form.email.data}', 'flash_error')
            return render_template("login.html", title="Login", form=form)

        login_user(valid_user, remember=form.remember.data)
        flash(f'Successful login for: {form.email.data}!', 'flash_success')
        return redirect(url_for('home'))
    return render_template("login.html", title="Login", form=form)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        # send password recovery link to the validated email address
        try:
            pyrebase_auth.send_password_reset_email(form.email.data)
            flash(f'A password recovery email has been sent to: {form.email.data}', 'flash_success')
        except:
            flash(f'Error sending recovery email for: {form.email.data}', 'flash_error')
        return redirect(url_for('home'))
    return render_template("forgot_password.html", title="Forgot Password", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/validate_user/<d>/", methods=['POST'])
def validate_user(d):
    return_value = "false"
    # Convert string parameter to JSON
    json_data = json.loads(d)
    email = json_data["EMAIL"]
    device_id = json_data["DEVICE_ID"]

    # Check to see if email is administrator / owner of sensor
    doc_ref = firestore_client.collection('users').document(email)
    doc = doc_ref.get().to_dict()
    if doc['admin']:
        return "true"       # remember must return a string not a bool

    # TODO Check FIREBASE for valid email and mac pair (Quang)
    # Properly format the DEVICE_ID from string MXXXXXXXXXXXX to XX:XX:XX:XX:XX:XX
    mac = device_id[1:3] + ":" + device_id[3:5] + ":" + device_id[5:7] + ":" + device_id[7:9] + ":" + device_id[9:11] + ":" + device_id[11:13]
    doc_ref = firestore_client.collection('sensor_owner').document(mac)
    doc = doc_ref.get().to_dict()
    try:
        if doc['email'] == email:
            return "true"
        else:
            return "false"
    except:
        return "false"


def my_converter(o):
    return o.__str__()


# Helper Functions ***************************************************************
def send_registration_email(form, email_link):
    try:
        msg = Message('airU Registration', sender=os.getenv("MAIL_USERNAME"), recipients=[form.email.data, os.getenv("MAIL_USERNAME")])
        msg.body = 'Test'
        msg.html = render_template("registration_email.html",
                               email=form.email.data,
                               first_name=form.first_name.data,
                               last_name=form.last_name.data,
                               street_address=form.street_address.data,
                               city_address=form.city.data,
                               state_address=form.state.data,
                               zip_address=form.zip_code.data,
                               email_link=email_link)
        mail.send(msg)
        return "sent"

    except Exception as e:
        return str(e)

# ***********************************************************
# Function: request_data_flask(d)
# Called by script.js
# Parameter:
# Return: Last recorded sensor input from all sensors in the DB
# ***********************************************************
@app.route("/request_data_flask/<d>/", methods=['GET'])
def request_data_flask(d):
    sensor_list = []
    # get the latest sensor data from each sensor
    q = ("SELECT `" + sensor_table + "`.DEVICE_ID, TIMESTAMP, PM1, PM25, PM10, LAT, LON, TEMP, CO, NOX, HUM, VER "
         "FROM `" + sensor_table + "` "
         "INNER JOIN (SELECT DEVICE_ID, MAX(TIMESTAMP) as maxts "
         "FROM `" + sensor_table + "` GROUP BY DEVICE_ID) mr "
         "ON `" + sensor_table + "`.DEVICE_ID = mr.DEVICE_ID AND TIMESTAMP = maxts;")

    query_job = bq_client.query(q)
    rows = query_job.result()  # Waits for query to finish
    for row in rows:
        sensor_list.append({"DEVICE_ID": str(row.DEVICE_ID),
                            "LAT": row.LAT,
                            "LON": row.LON,
                            "TIMESTAMP": str(row.TIMESTAMP),
                            "PM1": row.PM1,
                            "PM25": row.PM25,
                            "PM10": row.PM10,
                            "TEMP": row.TEMP,
                            "HUM": row.HUM,
                            "NOX": row.NOX,
                            "CO": row.CO,
                            "VER": row.VER})

    json_sensors = json.dumps(sensor_list, indent=4)
    return json_sensors


# ***********************************************************
# Function: request_historical(d)
# Called by script.js
# Parameter: JSON format containing DEVICE_ID and DAYS (number of days to query 1,3, or 7
# Return: JSON sensor data for the given sensor and given number of days
# ***********************************************************
@app.route("/request_historical/<d>/", methods=['GET'])
def request_historical(d):
    sensor_list = []
    json_data = json.loads(d)
    id = json_data["DEVICE_ID"]
    days = str(json_data["DAYS"])
    # get the latest sensor data from each sensor
    q = ("SELECT DATETIME_TRUNC(DATETIME(TIMESTAMP, 'America/Denver'), HOUR) AS D, ROUND(AVG(PM25),2) AS AVG_PM25 "
        "FROM `" + sensor_table + "` "
        "WHERE DEVICE_ID=\'" + id + "\' "
        "AND TIMESTAMP >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL " + days + " DAY) "
        "GROUP BY D ORDER BY D;")

    query_job = bq_client.query(q)
    rows = query_job.result()  # Waits for query to finish
    for row in rows:
        sensor_list.append({"D_TIME": row.D,
                            "AVG_PM25": row.AVG_PM25})

    json_sensors = json.dumps(sensor_list, default=my_converter, indent=4)
    return json_sensors


# ****************************************************************************************************************
# WEB API FOLLOWS-------------------------------------------------------------------------------------------------
# ****************************************************************************************************************


# ***********************************************************
# Function: request_sensor_data
# Called by script.js
# Query Parameters: device_id, days
# Return: JSON object ALL entries for the specified device in the past number of days
# ***********************************************************
@app.route("/request_sensor_data/", methods=['GET'])
def request_sensor_data():
    query_parameters = request.args
    device_id = query_parameters.get('device_id')
    if device_id == "all":
        device_id = ""
    elif device_id.find(',') > 0:
        # multiple device_id's exist - must parse
        device_id = "DEVICE_ID IN (" + parse_device_list(device_id) + ") AND "
    else:
        device_id = "DEVICE_ID =\'M" + device_id.upper() + "\' AND "

    days = int(query_parameters.get('days'))
    # Ensure valid number for query (no 0 or negatives)
    if days < 1:
        days = 1

    sensor_list = []
    # get the latest sensor data from each sensor
    q = ("SELECT DEVICE_ID, DATETIME_TRUNC(DATETIME(TIMESTAMP, 'America/Denver'), HOUR) AS D, ROUND(AVG(PM25),2) AS AVG_PM25 "
        "FROM `" + sensor_table + "` "
        "WHERE " + device_id + ""
        "TIMESTAMP >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL " + str(days) + " DAY) "
        "GROUP BY DEVICE_ID,D ORDER BY D;")

    query_job = bq_client.query(q)
    if query_job.error_result:
        return "Invalid API call - check documentation."
    rows = query_job.result()  # Waits for query to finish

    for row in rows:
        sensor_list.append({"device_id": row.DEVICE_ID,
                            "date_time": row.D,
                            "avg_pm25": row.AVG_PM25})

    json_sensors = json.dumps(sensor_list, default=my_converter, indent=4)
    return jsonify(sensor_list)


def parse_device_list(device_list):
    # add 'M' to all MAC addresses
    new_string = ""
    device_list_string = device_list.split(',')
    for i in range(len(device_list_string)):
        new_string += "\'M" + device_list_string[i].upper().strip() + "\',"
    # remove last ',' in string - it will be the last character
    new_string = new_string[:len(new_string)-1]
    return new_string
