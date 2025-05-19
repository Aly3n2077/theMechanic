from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, TimeField, DateField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class VehicleForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    license_plate = StringField('License Plate', validators=[DataRequired(), Length(max=20)])

class BookingForm(FlaskForm):
    mechanic_id = HiddenField('Mechanic ID', validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    vehicle_id = SelectField('Vehicle', coerce=int, validators=[DataRequired()])
    booking_date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    booking_time = SelectField('Time', validators=[DataRequired()])
    issue_description = TextAreaField('Describe the issue', validators=[DataRequired(), Length(max=500)])
