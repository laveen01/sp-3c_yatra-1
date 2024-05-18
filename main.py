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
from flask import abort, make_response
import os
from dotenv import load_dotenv
import psycopg2
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SelectField, SubmitField, PasswordField, validators, IntegerField
import requests
from wtforms.validators import DataRequired, URL
from sqlalchemy import and_, func, or_
import csv
import io


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
naklank1_double_bed_max_count = 22

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
            if current_user.email != 'view_all_bookings@gmail.com':
                return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

##CONFIGURE TABLES

class HotelList(db.Model):
    __tablename__ = "hotel_lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    booked = db.Column(db.Float)
    cancelled = db.Column(db.Float)

    @property
    def available(self):
        return self.quantity - self.booked + self.cancelled


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)
    area = db.Column(db.String, nullable=False)
    mobile = db.Column(db.String, nullable=False)


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_area = db.Column(db.String, nullable=False)
    user_mobile = db.Column(db.String, nullable=False)
    user_email = db.Column(db.String, nullable=False)
    date_time = db.Column(db.String, nullable=False)
    hotel = db.Column(db.String, nullable=False)
    room_type = db.Column(db.String, nullable=False)
    booking_type = db.Column(db.String, nullable=False)
    number_of_room_booked = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.String, nullable=False)
    transaction_date = db.Column(db.String)
    utr_receipt_number = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    cancellation_date = db.Column(db.String)
    verification_date = db.Column(db.String)
    room_no = db.Column(db.String)


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
    max_quantity=22  #double-bed max count in Building 1 should be 22, total of 2 bed & 3 bed is 35

    form = DoBookingHotelForm()
    print(f"form is {form}")
    if form.validate_on_submit():

        global name_of_hotel
        global naklank1_double_bed_max_count

        if len(name_of_hotel) == 0:
            x=0
            print('hi')
            name_of_hotel = form.hotel_name.data
            choices = HotelChoices.hotel_description(name_of_hotel)
            return render_template("do_booking.html", hotel=name_of_hotel, form=form, choices=choices, logged_in=current_user.is_authenticated, current_user=current_user, x=x, max_quantity=max_quantity)

    if len(name_of_hotel) != 0:
        x=1
        # count of rooms for 2 bed & complete and single to be taken
        naklank1_double_bed_count = (((db.session.query(func.sum(Booking.number_of_room_booked))
                                        .filter(Booking.hotel == 'Naklank Building 1',Booking.room_type == 'Double',Booking.booking_type == 'complete room',Booking.status != 'Cancelled').scalar() or 0))

                                     +
                                    ((db.session.query(func.sum(Booking.number_of_room_booked))
                                        .filter(Booking.hotel == 'Naklank Building 1', Booking.room_type == 'Double', Booking.booking_type == 'prjis bed',Booking.status != 'Cancelled').scalar() or 0)/2)

                                    +

                                    ((db.session.query(func.sum(Booking.number_of_room_booked))
                                        .filter(Booking.hotel == 'Naklank Building 1', Booking.room_type == 'Double', Booking.booking_type == 'matajis bed', Booking.status != 'Cancelled').scalar() or 0)/2))

        if not naklank1_double_bed_count:
            naklank1_double_bed_count = 0
        # print(f'total sum is {total_sum}')
        max_quantity = naklank1_double_bed_max_count - naklank1_double_bed_count
        roomDesc = request.form.get("description")
        hotelName = request.form.get("hotel")
        type_of_room = request.form.get("type_of_room")
        print(type_of_room)
        number_of_room = HotelChoices.room_availability(hotelName,roomDesc)
        name_of_hotel = ""
        if number_of_room and number_of_room.quantity is not None and number_of_room.booked is not None:
            if number_of_room.quantity > (number_of_room.booked - number_of_room.cancelled):
                max_quantity = number_of_room.quantity - number_of_room.booked + number_of_room.cancelled
                return render_template("do_booking.html", hotel=hotelName, form=form, description=roomDesc, quantity=number_of_room, type_of_room=type_of_room, logged_in=current_user.is_authenticated, current_user=current_user, naklank1_double_bed_count=naklank1_double_bed_count, naklank1_double_bed_max_count=naklank1_double_bed_max_count, x=x, max_quantity=max_quantity)
            else:
                return render_template("do_booking.html", hotel=hotelName, form=form, description=roomDesc, message="No rooms Available", type_of_room=type_of_room, logged_in=current_user.is_authenticated, current_user=current_user, naklank1_double_bed_count=naklank1_double_bed_count, naklank1_double_bed_max_count=naklank1_double_bed_max_count, x=x, max_quantity=max_quantity)
        else:
            return render_template("do_booking.html", form=form, logged_in=current_user.is_authenticated,
                                   current_user=current_user, naklank1_double_bed_count=naklank1_double_bed_count, naklank1_double_bed_max_count=naklank1_double_bed_max_count, x=x, max_quantity=max_quantity)

    return render_template("do_booking.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user, max_quantity=max_quantity)

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
            booking_type=request.form.get("booking_type"),
            number_of_room_booked=request.form.get("quantity_booked"),
            amount_paid=request.form.get("amount_paid"),
            transaction_date=request.form.get("transaction_date"),
            utr_receipt_number=request.form.get("utr"),
            status="To be verified",
        )
        db.session.add(new_booking)
        db.session.commit() #adding data in booking list
        hotel_list = HotelList.query.filter_by(name=request.form.get("hotel"), description=request.form.get("description")).first()

        if request.form.get("hotel") != 'Naklank Building 3' and request.form.get("booking_type") != 'complete room':
            if request.form.get("room_type") == 'Double':
                hotel_list.booked = float(float(request.form.get("already_booked")) + float(float(request.form.get("quantity_booked"))/2))
            else:
                hotel_list.booked = float(float(request.form.get("already_booked")) + float(float(request.form.get("quantity_booked")) / 3))
        else:
            hotel_list.booked = float(float(request.form.get("already_booked")) + float(request.form.get("quantity_booked")))

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

        room_type_cancld = cancelled_booking.room_type
        booking_type_cancld = cancelled_booking.booking_type
        db.session.commit() #updating the booking status as Cancelled

        # Retrieve the hotel and the number of cancelled rooms
        hotel_name = request.form.get("hotel")
        hotel = HotelList.query.filter_by(name=hotel_name).first()
        cancelled_rooms = hotel.cancelled

        # Update the number of cancelled rooms
        if room_type_cancld != 'sharing' and booking_type_cancld != 'complete room':
            if room_type_cancld == 'Double':
                cancelled_rooms += float(float(request.form.get("number_of_room_booked"))/2)
            else:
                cancelled_rooms += float(float(request.form.get("number_of_room_booked")) / 3)
        else:
            cancelled_rooms += float(request.form.get("number_of_room_booked"))  # Assuming one room is cancelled at a time

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

@app.route('/download_data_excel')
def download_data_excel():
    bookings = Booking.query.all()

    # Create a CSV buffer to write data
    output = io.StringIO()
    writer = csv.writer(output)

    # Write column headings
    writer.writerow([
        'Booking ID', 'User', 'Area', 'Email', 'Mobile', 'Hotel', 'Room Type',
        'Booking Type', 'Booked Qty', 'Amount Paid', 'Transaction Date',
        'Ref Number', 'Status', 'Verification Date', 'Cancellation Date',
        'Room No'
    ])

    # Write data rows
    for booking in bookings:
        writer.writerow([
            booking.id, booking.user_name, booking.user_area, booking.user_email,
            booking.user_mobile, booking.hotel, booking.room_type,
            booking.booking_type, booking.number_of_room_booked, booking.amount_paid,
            booking.transaction_date, booking.utr_receipt_number, booking.status,
            booking.verification_date, booking.cancellation_date, booking.room_no
        ])

    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=bookings.csv"
    response.headers["Content-type"] = "text/csv"

    return response

@app.route('/download_hotel_booking_status')
def download_hotel_booking_status():
    hotels = HotelList.query.all()

    # Create a CSV buffer to write data
    output = io.StringIO()
    writer = csv.writer(output)

    # Write column headings
    writer.writerow([
        'Hotel ID', 'Name', 'Description', 'Category', 'Quantity', 'Booked', 'Cancelled',
    ])

    # Write data rows
    for hotel in hotels:
        writer.writerow([
            hotel.id, hotel.name, hotel.description, hotel.category,
            hotel.quantity, hotel.booked, hotel.cancelled,
        ])

    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=bookings.csv"
    response.headers["Content-type"] = "text/csv"

    return response


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
