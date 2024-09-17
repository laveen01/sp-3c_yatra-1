from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, validators, IntegerField
from wtforms.validators import DataRequired, URL, NumberRange, Length, Regexp
from flask_ckeditor import CKEditorField


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# Assuming congregational_areas is defined like this
congregational_areas = [
    ("area1", "Area 1"),
    ("area2", "Area 2"),
    ("area3", "Area 3")
    # Add more areas as needed
]

area_leaders = [
    ("leader1", "Leader 1"),
    ("leader2", "Leader 2"),
    ("leader3", "Leader 3")
    # Add more leaders as needed
]

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    area = SelectField("Area / Congregation Name", choices=congregational_areas, validators=[DataRequired()])
    area_leader = SelectField("Area Leader", choices=area_leaders, validators=[DataRequired()])
    mobile = StringField("Mobile Number", validators=[
        DataRequired(),
        Length(min=10, max=10, message="Mobile number must be exactly 10 digits long"),
        Regexp(r'^[0-9]+$', message="Mobile number must contain only digits")
    ])
    email = StringField("Email", [validators.DataRequired(), validators.Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")

class LoginForm(FlaskForm):
    email = StringField("Email", [validators.DataRequired(), validators.Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log Me In!")

class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

class AddHotelForm(FlaskForm):
    name = StringField("Hotel Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    category = SelectField("Category of Room", choices=["Super-Deluxe", "Deluxe", "General", "Dormitory"], validators=[DataRequired()])
    quantity = IntegerField("Total Number Available", validators=[DataRequired()])
    booked = IntegerField("Total Booked", validators=[NumberRange(min=0)])
    cancelled = IntegerField("Total Cancelled", validators=[NumberRange(min=0)])
    price_3_day = IntegerField("Price_3_day", validators=[DataRequired()])
    price_2_day = IntegerField("Price_2_day", validators=[DataRequired()])
    submit = SubmitField("Add Hotel")
    # occupancy = StringField("Occupancy", validators=[DataRequired()])
    # occupancy1 = StringField("Occupancy1", validators=[DataRequired()])
    # occupancy2 = StringField("Occupancy2", validators=[DataRequired()])




