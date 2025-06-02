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
    ('Aurangabad', 'Aurangabad'),
    ('Ayodhya', 'Ayodhya'),
    ('Bareilly', 'Bareilly'),
    ('Bihar - Darbhanga', 'Bihar - Darbhanga'),
    ('Bihar - Gaya', 'Bihar - Gaya'),
    ('Bihar - Madhubani', 'Bihar - Madhubani'),
    ('Durg', 'Durg'),
    ('Etah', 'Etah'),
    ('Gzbd - BBT', 'Gzbd - BBT'),
    ('GZB Crossing Republic', 'GZB Crossing Republic'),
    ('Ghaziabad Food For Life', 'Ghaziabad Food For Life'),
    ('Ghaziabad Fund Raising', 'Ghaziabad Fund Raising'),
    ('GZB Golf Link', 'GZB Golf Link'),
    ('GZB Govindpuram', 'GZB Govindpuram'),
    ('GZB Mohan Nagar', 'GZB Mohan Nagar')
    ('Ghaziabad IGF ', 'Ghaziabad IGF '),
    ('GZB Raj Nagar Extn', 'GZB Raj Nagar Extn'),
    ('Ghaziabad Temple', 'Ghaziabad Temple'),
    ('GZB Vijay Nagar', 'GZB Vijay Nagar'),
    ('GZB Wave City', 'GZB Wave City'),
    ('Ghaziabad - Others', 'Ghaziabad - Others'),
    ('Gurugram', 'Gurugram'),
    ('Hapur', 'Hapur'),
    ('Hathras', 'Hathras'),
    ('Kathwada', 'Kathwada'),
    ('Kiccha', 'Kiccha'),
    ('Lucknow', 'Lucknow'),
    ('Mainpuri', 'Mainpuri'),
    ('Meerut', 'Meerut'),
    ('Moradabad', 'Moradabad'),
    ('Muzaffarnagar', 'Muzaffarnagar'),
    ('Pilakhuwa', 'Pilakhuwa'),
    ('Pilibhit', 'Pilibhit'),
    ('Raipur', 'Raipur'),
    ('Rudrapur', 'Rudrapur'),
    ('Saharanpur', 'Saharanpur'),
    ('Sahibabad', 'Sahibabad'),
    ('Shajahanpur', 'Shajahanpur'),
    ('SNS', 'SNS'),
    # Add more areas as needed
]

area_leaders = [
    ('HG Abhay Achyuta Pr', 'HG Abhay Achyuta Pr'),
    ('HG Achintya Sukta Pr', 'HG Achintya Sukta Pr'),
    ('HG Adhoksaja Dham Pr', 'HG Adhoksaja Dham Pr'),
    ('HG Adikarta Vandan Pr', 'HG Adikarta Vandan Pr'),
    ('HG Aditya Narayan Pr', 'HG Aditya Narayan Pr'),
    ('HG Agnirupa Nrsimha Pr', 'HG Agnirupa Nrsimha Pr'),
    ('HG Anant Shyam Pr', 'HG Anant Shyam Pr'),
    ('HG Bhim Arjuna Pr', 'HG Bhim Arjuna Pr'),
    ('HG Chittranjan Pr', 'HG Chittranjan Pr'),
    ('HG Damodar Lila Pr', 'HG Damodar Lila Pr'),
    ('HG Dayalu Kanhai Pr', 'HG Dayalu Kanhai Pr'),
    ('HG Dev Nitai Pr', 'HG Dev Nitai Pr'),
    ('HG Gaurvigraha Priya Pr', 'HG Gaurvigraha Priya Pr'),
    ('HG Giri Mohan Pr', 'HG Giri Mohan Pr'),
    ('HG Hansa Avtar Pr', 'HG Hansa Avtar Pr'),
    ('HG Krishna Radhika Mata ji', 'HG Krishna Radhika Mata ji'),
    ('HG Laxman Kripa Pr', 'HG Laxman Kripa Pr'),
    ('HG Madhav Gaur Pr', 'HG Madhav Gaur Pr'),
    ('HG Mahaman Nitai Pr', 'HG Mahaman Nitai Pr'),
    ('HG Murari Archan Pr', 'HG Murari Archan Pr'),
    ('HG Naveen Gaur Pr', 'HG Naveen Gaur Pr'),
    ('HG Nitya Mahaman Pr', 'HG Nitya Mahaman Pr'),
    ('HG Paramsiddhi mataji', 'HG Paramsiddhi mataji'),
    ('HG Parmeshwar Hari Pr', 'HG Parmeshwar Hari Pr'),
    ('HG Radhakant Pr', 'HG Radhakant Pr'),
    ('HG Radhikeshwar Pr', 'HG Radhikeshwar Pr'),
    ('HG Ram Kumar Pr', 'HG Ram Kumar Pr'),
    ('HG Sachinandan Prem Pr', 'HG Sachinandan Prem Pr'),
    ('HG Sadhu Jeevan Pr', 'HG Sadhu Jeevan Pr'),
    ('HG Sahishuna Vipra Pr', 'HG Sahishuna Vipra Pr'),
    ('HG Satya Bhanu Pr', 'HG Satya Bhanu Pr'),
    ('HG Sevya Girdhari Pr', 'HG Sevya Girdhari Pr'),
    ('HG Shashipriya Nath Pr', 'HG Shashipriya Nath Pr'),
    ('HG Shatbhuj Gaur Pr', 'HG Shatbhuj Gaur Pr'),
    ('HG Shyam Karuna Pr', 'HG Shyam Karuna Pr'),
    ('HG Sundar Anand Pr', 'HG Sundar Anand Pr'),
    ('HG Ujjwal Sundar Pr', 'HG Ujjwal Sundar Pr'),
    ('HG Vakresvara Madhava Pr', 'HG Vakresvara Madhava Pr'),
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




