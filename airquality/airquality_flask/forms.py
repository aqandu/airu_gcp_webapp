from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from airquality_flask import firebase_auth, ds_client


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    street_address = StringField('Street Address', validators=[DataRequired(), Length(min=2, max=20)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=20)])
    zip_code = StringField('Zip Code', validators=[DataRequired(), Length(5)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit Registration')

    def validate_email(self, email):
        # Query DATASTORE to ensure email address is not already in use
        # Query a user with a key (generate the key from kind and unique name)
        user = ds_client.get(ds_client.key('Users', email.data))
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        else:
            # Check if credentials already exist in Authentication
            try:
                firebase_auth.get_user_by_email(email)
                raise ValidationError('That email is taken. Please choose a different one.')
            except:
                # We want the exception to be thrown - this indicates no email exists
                pass


        # # LEGACY ##################################################################################
        # # Query FIRESTORE to see if email is already in use
        # # If email is already in use - send validation error to select another email
        # doc_ref = firestore_client.collection('users').document(email.data)
        # doc = doc_ref.get()
        # if doc.exists:
        #     raise ValidationError('That email is taken. Please choose a different one.')
        # else:
        #     # Check if credentials already exist in Authentication
        #     try:
        #         firestore_auth.get_user_by_email(email)
        #         raise ValidationError('That email is taken. Please choose a different one.')
        #     except:
        #         # We want the exception to be thrown - this indicates no email exists
        #         pass


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_email(self, email):
        # validate that the email exists with FIREBASE authentication
        try:
            user = firebase_auth.get_user_by_email(email.data)
            if not user.email_verified:
                raise ValidationError('Email has not been verified.')
        except:
            raise ValidationError('Email address not found - try again.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send password recovery email')

    def validate_email(self, email):
        # validate that the email exists with FIREBASE
        try:
            user = firebase_auth.get_user_by_email(email.data)
            if not user.email_verified:
                raise ValidationError('Email has not been verified.')
        except:
            raise ValidationError('Email address not found - try again.')