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
    ('Ayodhya', 'Ayodhya'),
    ('Bareilly', 'Bareilly'),
    ('Bihar - Gaya', 'Bihar - Gaya'),
    ('Bihar - Madhubani', 'Bihar - Madhubani'),
    ('Gzbd - BBT', 'Gzbd - BBT'),
    ('GZB Crossing Republic', 'GZB Crossing Republic'),
    ('Ghaziabad Fund Raising', 'Ghaziabad Fund Raising'),
    ('GZB Govindpuram', 'GZB Govindpuram'),
    ('Ghaziabad IGF ', 'Ghaziabad IGF '),
    ('Ghaziabad Temple', 'Ghaziabad Temple'),
    ('GZB Temple Fund Raising', 'GZB Temple Fund Raising'),
    ('GZB Vijay Nagar', 'GZB Vijay Nagar'),
    ('GZB Wave City', 'GZB Wave City'),
    ('Ghaziabad - Others', 'Ghaziabad - Others'),
    ('Gurugram', 'Gurugram'),
    ('Hathras', 'Hathras'),
    ('Kathwada', 'Kathwada'),
    ('Lucknow', 'Lucknow'),
    ('Meerut', 'Meerut'),
    ('Moradabad', 'Moradabad'),
    ('Pilakhuwa', 'Pilakhuwa'),
    ('Pilibhit', 'Pilibhit'),
    ('Rudrapur', 'Rudrapur'),
    ('Sahibabad', 'Sahibabad'),
    ('Shajahanpur', 'Shajahanpur'),
    ('SNS', 'SNS'),
    # Add more areas as needed
]

area_leaders = [
    ('HG Abhiram Govind Pr', 'HG Abhiram Govind Pr'),
    ('HG Achintya Sukta Pr', 'HG Achintya Sukta Pr'),
    ('HG Adhoksaja Dham Pr', 'HG Adhoksaja Dham Pr'),
    ('HG Adikarta Vandan Pr', 'HG Adikarta Vandan Pr'),
    ('HG Aditya Narayan Pr', 'HG Aditya Narayan Pr'),
    ('HG Agnirupa Nrsimha Pr', 'HG Agnirupa Nrsimha Pr'),
    ('HG Bhim Arjuna Pr', 'HG Bhim Arjuna Pr'),
    ('HG Chittranjan Pr', 'HG Chittranjan Pr'),
    ('HG Damodar Leela Pr', 'HG Damodar Leela Pr'),
    ('HG Dayalu Kanhai Pr', 'HG Dayalu Kanhai Pr'),
    ('HG Dev Nitai Pr', 'HG Dev Nitai Pr'),
    ('HG Giri Mohan Pr', 'HG Giri Mohan Pr'),
    ('HG Hansa Avtar Pr', 'HG Hansa Avtar Pr'),
    ('HG Laxman Kripa Pr', 'HG Laxman Kripa Pr'),
    ('HG Madhav Gaur Pr', 'HG Madhav Gaur Pr'),
    ('HG Mahaman Nitai Pr', 'HG Mahaman Nitai Pr'),
    ('HG Nitya Mahaman Pr', 'HG Nitya Mahaman Pr'),
    ('HG Paramsiddhi mataji', 'HG Paramsiddhi mataji'),
    ('HG Ram Kumar Pr', 'HG Ram Kumar Pr'),
    ('HG Sachinandan Prem Pr', 'HG Sachinandan Prem Pr'),
    ('HG Sadhu Jeevan Pr', 'HG Sadhu Jeevan Pr'),
    ('HG Sahishuna Vipra Pr', 'HG Sahishuna Vipra Pr'),
    ('HG Satya Bhanu Pr', 'HG Satya Bhanu Pr'),
    ('HG Sevya Girdhari Pr', 'HG Sevya Girdhari Pr'),
    ('HG Shashipriya Nath Pr', 'HG Shashipriya Nath Pr'),
    ('HG Shatbhuj Gaur Pr', 'HG Shatbhuj Gaur Pr'),
    ('HG Shyam Karuna Pr', 'HG Shyam Karuna Pr'),
    ('HG Ujjwal Sundar Pr', 'HG Ujjwal Sundar Pr'),
    ('HG Vakresvara Madhava Pr', 'HG Vakresvara Madhava Pr'),
    ('Rakshak Pr', 'Rakshak Pr'),
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

class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", [validators.DataRequired(), validators.Email()])
    submit = SubmitField("Submit")

class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

class AddCategoryForm(FlaskForm):
    name = SelectField("Category of Room", choices=["Super-Deluxe", "Deluxe", "General", "Dormitory"], validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    # category = SelectField("Category of Room", choices=["Super-Deluxe", "Deluxe", "General", "Dormitory"], validators=[DataRequired()])
    # quantity = IntegerField("Total Number Available", validators=[DataRequired()])
    booked = IntegerField("Total Booked", validators=[NumberRange(min=0)])
    cancelled = IntegerField("Total Cancelled", validators=[NumberRange(min=0)])
    price_yatra = IntegerField("Yatra_Price", validators=[DataRequired()])
    price_yatra_child = IntegerField("Yatra_Price_Child", validators=[DataRequired()])
    # price_2_day = IntegerField("Price_2_day", validators=[DataRequired()])
    submit = SubmitField("Add Category")
    # occupancy = StringField("Occupancy", validators=[DataRequired()])
    # occupancy1 = StringField("Occupancy1", validators=[DataRequired()])
    # occupancy2 = StringField("Occupancy2", validators=[DataRequired()])




