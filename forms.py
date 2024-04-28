from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, validators, IntegerField
from wtforms.validators import DataRequired, URL, NumberRange
from flask_ckeditor import CKEditorField


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    area = StringField("Area", validators=[DataRequired()])
    mobile = StringField("Mobile Number", validators=[DataRequired()])
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
    category = SelectField("Category of Room", choices=["Super-Deluxe", "Deluxe non-AC", "Deluxe Sharing"], validators=[DataRequired()])
    quantity = IntegerField("Total Number Available", validators=[DataRequired()])
    booked = IntegerField("Total Booked", validators=[NumberRange(min=0)])
    cancelled = IntegerField("Total Cancelled", validators=[NumberRange(min=0)])
    submit = SubmitField("Add Hotel")
    # occupancy = StringField("Occupancy", validators=[DataRequired()])
    # occupancy1 = StringField("Occupancy1", validators=[DataRequired()])
    # occupancy2 = StringField("Occupancy2", validators=[DataRequired()])




