from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, FloatField, HiddenField, DateField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_mechanic = BooleanField('Register as a Mechanic')
    submit = SubmitField('Register')

class VehicleForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    license_plate = StringField('License Plate', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Add Vehicle')

class BookingForm(FlaskForm):
    mechanic_id = HiddenField('Mechanic ID', validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    vehicle_id = SelectField('Vehicle', coerce=int, validators=[DataRequired()])
    booking_date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    booking_time = SelectField('Time', validators=[DataRequired()])
    issue_description = TextAreaField('Describe the issue', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Book Appointment')

class ReviewForm(FlaskForm):
    booking_id = HiddenField('Booking ID', validators=[DataRequired()])
    mechanic_id = HiddenField('Mechanic ID', validators=[DataRequired()])
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], 
                        coerce=int, validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Your Review', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Review')

class VehicleListingForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    price = FloatField('Price (USD)', validators=[DataRequired(), NumberRange(min=0)])
    condition = SelectField('Condition', choices=[
        ('New', 'New'), 
        ('Used', 'Used'), 
        ('Certified Pre-Owned', 'Certified Pre-Owned')
    ], validators=[DataRequired()])
    mileage = IntegerField('Mileage', validators=[DataRequired(), NumberRange(min=0)])
    color = StringField('Color', validators=[DataRequired(), Length(max=30)])
    transmission = SelectField('Transmission', choices=[
        ('Automatic', 'Automatic'), 
        ('Manual', 'Manual'), 
        ('Semi-Automatic', 'Semi-Automatic')
    ], validators=[DataRequired()])
    fuel_type = SelectField('Fuel Type', choices=[
        ('Petrol', 'Petrol'), 
        ('Diesel', 'Diesel'), 
        ('Electric', 'Electric'), 
        ('Hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20, max=1000)])
    features = StringField('Features (comma separated)', validators=[Optional()])
    images = MultipleFileField('Vehicle Images', validators=[Optional()])
    submit = SubmitField('List Vehicle')

class VehicleSearchForm(FlaskForm):
    make = StringField('Make', validators=[Optional()])
    model = StringField('Model', validators=[Optional()])
    min_year = IntegerField('Min Year', validators=[Optional(), NumberRange(min=1900, max=2100)])
    max_year = IntegerField('Max Year', validators=[Optional(), NumberRange(min=1900, max=2100)])
    min_price = FloatField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[Optional(), NumberRange(min=0)])
    condition = SelectField('Condition', choices=[
        ('', 'Any'), 
        ('New', 'New'), 
        ('Used', 'Used'), 
        ('Certified Pre-Owned', 'Certified Pre-Owned')
    ], validators=[Optional()])
    submit = SubmitField('Search')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    bio = TextAreaField('About Me', validators=[Optional(), Length(max=500)])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Save Changes')