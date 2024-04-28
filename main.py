import flask
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, AddHotelForm
from flask_gravatar import Gravatar
from functools import wraps
from flask import abort
import os
from dotenv import load_dotenv
import psycopg2
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SelectField, SubmitField, PasswordField, validators, IntegerField
import requests
from wtforms.validators import DataRequired, URL
from sqlalchemy import and_


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)
csrf = CSRFProtect(app)

##CONNECT TO DB
if os.environ.get("LOCAL") == "True":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SP3C_Kartik_Yatra.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

#global variables for booking
name_of_hotel = ""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

def account_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 2:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id > 2:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

##CONFIGURE TABLES

class HotelList(db.Model):
    __tablename__ = "hotel_lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    booked = db.Column(db.Integer)
    cancelled = db.Column(db.Integer)

    @property
    def available(self):
        return self.quantity - self.booked + self.cancelled
    # occupancy = db.Column(db.String(50), nullable=False)
    # occupancy1 = db.Column(db.String(50), nullable=False)
    # occupancy2 = db.Column(db.String(50), nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(100), nullable=False)


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_area = db.Column(db.String(50), nullable=False)
    user_mobile = db.Column(db.String(15), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.String(100), nullable=False)
    hotel = db.Column(db.String(50), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    number_of_room_booked = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.String(20), nullable=False)
    transaction_date = db.Column(db.String(20))
    utr_receipt_number = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    cancellation_date = db.Column(db.String(25))
    verification_date = db.Column(db.String(20))
    room_no = db.Column(db.String(10))


db.create_all()

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

class HotelChoices():
    def __init__(self):
        pass
    def hotel_name(self):
        hotel_names = []
        names = db.session.query(HotelList.name).distinct()
        for name in names:
            hotel_names.append(name.name)
        return(hotel_names)
    def hotel_description(hotel):
        descriptions = []
        desc = HotelList.query.filter_by(name=hotel).all()
        for des in desc:
            descriptions.append(des.description)
        return (descriptions)

    def room_availability(hotel, description):
        total_rooms = HotelList.query.filter_by(name=hotel, description=description).first()
        return total_rooms

class DoBookingHotelForm(FlaskForm):
    hotel_name = SelectField("Hotel Name", choices=HotelChoices.hotel_name(self=""), validators=[DataRequired()])
    submit = SubmitField("Select Hotel")

@app.route('/')
def home():

    return render_template("index.html", logged_in=current_user.is_authenticated, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=12
        )
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hash_and_salted_password,
            area=form.area.data,
            mobile=form.mobile.data,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/do_booking', methods=["GET", "POST"])
def do_booking():

    form = DoBookingHotelForm()
    print(f"form is {form}")
    if form.validate_on_submit():

        global name_of_hotel
        if len(name_of_hotel) == 0:

            name_of_hotel = form.hotel_name.data
            choices = HotelChoices.hotel_description(name_of_hotel)
            return render_template("do_booking.html", hotel=name_of_hotel, form=form, choices=choices, logged_in=current_user.is_authenticated, current_user=current_user)

    if len(name_of_hotel) != 0:

        roomDesc = request.form.get("description")
        hotelName = request.form.get("hotel")
        number_of_room = HotelChoices.room_availability(hotelName,roomDesc)
        name_of_hotel = ""
        if number_of_room and number_of_room.quantity is not None and number_of_room.booked is not None:
            if number_of_room.quantity > number_of_room.booked:
                return render_template("do_booking.html", hotel=hotelName, form=form, description=roomDesc, quantity=number_of_room, logged_in=current_user.is_authenticated, current_user=current_user)
            else:
                return render_template("do_booking.html", hotel=hotelName, form=form, description=roomDesc, message="No rooms Available", logged_in=current_user.is_authenticated, current_user=current_user)
        else:
            return render_template("do_booking.html", form=form, logged_in=current_user.is_authenticated,
                                   current_user=current_user)
    return render_template("do_booking.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user)

@app.route('/book_room', methods=["GET", "POST"])
def book_room():
    if request.method == "POST":
        current_date_time = datetime.now()

        new_booking = Booking(
            user_id=request.form.get("user_id"),
            user_name=request.form.get("user_name"),
            user_area=request.form.get("user_area"),
            user_mobile=request.form.get("user_mobile"),
            user_email=request.form.get("user_email"),
            date_time=current_date_time,
            hotel=request.form.get("hotel"),
            room_type=request.form.get("room_type"),
            number_of_room_booked=request.form.get("quantity_booked"),
            amount_paid=request.form.get("amount_paid"),
            transaction_date=request.form.get("transaction_date"),
            utr_receipt_number=request.form.get("utr"),
            status="To be verified",
        )
        db.session.add(new_booking)
        db.session.commit() #adding data in booking list
        hotel_list = HotelList.query.filter_by(name=request.form.get("hotel"), description=request.form.get("description")).first()
        hotel_list.booked = int(int(request.form.get("already_booked")) + int(request.form.get("quantity_booked")))
        db.session.commit() #updating booked column  in hotel list
        return render_template("index.html", logged_in=current_user.is_authenticated, current_user=current_user)

    if request.method == "GET":
        return redirect(url_for('home'))

@app.route('/review_booking', methods=["GET", "POST"])
def review_booking():
    my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("review_booking.html", bookings=my_bookings, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route('/update_booking', methods=["GET", "POST"])
def update_booking():

    if request.method == 'POST':

        if request.form.get("form_purpose") == "publish_for_update":
            update_booking = Booking.query.filter_by(id=request.form.get("booking_id")).first()
            return render_template("update_booking.html", booking=update_booking, logged_in=current_user.is_authenticated, current_user=current_user)

        elif request.form.get("form_purpose") == "update_fields":
            updated_booking = Booking.query.filter_by(id=request.form.get("booking_id")).first()
            updated_booking.amount_paid = request.form.get("amount_paid")
            updated_booking.transaction_date = request.form.get("transaction_date")
            updated_booking.utr_receipt_number = request.form.get("utr_receipt_number")
            db.session.commit()

            my_bookings = Booking.query.filter_by(user_id=current_user.id).all()

            return render_template("review_booking.html", bookings=my_bookings, logged_in=current_user.is_authenticated,
                                   current_user=current_user)
    else:
        return render_template("index.html", logged_in=current_user.is_authenticated, current_user=current_user)


@app.route('/cancel_booking', methods=["GET", "POST"])
def cancel_booking():
    if request.method == 'POST':
        cancelled_date_time = datetime.now()

        cancelled_booking = Booking.query.filter_by(id=request.form.get("booking_id")).first()
        cancelled_booking.status = "Cancelled"
        cancelled_booking.cancellation_date = cancelled_date_time

        db.session.commit() #updating the booking status as Cancelled

        # Retrieve the hotel and the number of cancelled rooms
        hotel_name = request.form.get("hotel")
        hotel = HotelList.query.filter_by(name=hotel_name).first()
        cancelled_rooms = hotel.cancelled

        # Update the number of cancelled rooms
        cancelled_rooms += int(request.form.get("number_of_room_booked"))  # Assuming one room is cancelled at a time
        hotel.cancelled = cancelled_rooms
        db.session.commit()  # Update the cancelled rooms in the hotel list

        # Fetch the bookings for the current user
        my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
        return render_template("review_booking.html", bookings=my_bookings, logged_in=current_user.is_authenticated, current_user=current_user)

    else:
        return render_template("index.html", logged_in=current_user.is_authenticated, current_user=current_user)

@app.route('/verify_booking', methods=["GET", "POST"])
@account_only
def verify_booking():
    current_date_time = datetime.now()

    if request.method == "POST":
        verified_post = Booking.query.filter_by(id=request.form.get("booking_id")).first()
        verified_post.status = "Verified"
        verified_post.verification_date = current_date_time
        db.session.commit()
    to_be_verified = Booking.query.filter_by(status="To be verified").all()
    return render_template("verify_booking.html", bookings_tbv=to_be_verified, logged_in=current_user.is_authenticated, current_user=current_user)

@app.route('/view_all_booking', methods=["GET", "POST"])
@admin_only
def view_all_booking():
    all_bookings = Booking.query.all()

    return render_template("view_all_booking.html", bookings=all_bookings, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                text=form.comment_text.data,
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
        else:
            flash("Please login/register, for posting comments")
            return redirect(url_for('login'))
    return render_template("post.html", post=requested_post, form=form, logged_in=current_user.is_authenticated, current_user=current_user)

@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated, current_user=current_user)

@app.route("/add_hotels", methods=["GET", "POST"])
@admin_only
def add_hotels():
    form = AddHotelForm()
    if form.validate_on_submit():
        new_hotel = HotelList(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            quantity=form.quantity.data,
            booked=form.booked.data,
            cancelled=form.cancelled.data,
            # occupancy=form.occupancy.data,
            # occupancy1=form.occupancy1.data,
            # occupancy2=form.occupancy2.data,
        )
        db.session.add(new_hotel)
        db.session.commit()
        return redirect(url_for("hotel_details"))
    return render_template("add_hotel.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route("/hotel")
def hotel_details():
    hotels = HotelList.query.all()
    return render_template("hotels.html", hotels=hotels, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)
