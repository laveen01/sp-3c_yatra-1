import flask
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, ForgotPasswordForm, CommentForm, AddCategoryForm
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
import string
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
children_charges = 3500
email_address = os.environ.get("EMAIL_ADDRESS")
email_password = os.environ.get("EMAIL_PASSWORD")

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
        #If id is not 1 or EMAIL - VIEW_ALL_BOOKINGS@GMAIL.COM (creadted to specifically look into all the bookings done till now, shared to all area leaders) then return abort with 403 error
        if current_user.id > 2:
            if current_user.email != 'view_all_bookings@gmail.com':
                return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

##CONFIGURE TABLES

class CategoryList(db.Model):
    __tablename__ = "category_lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    # category = db.Column(db.String, nullable=False)
    # quantity = db.Column(db.Integer, nullable=False)
    booked = db.Column(db.Float)
    cancelled = db.Column(db.Float)
    price_yatra = db.Column(db.Integer, nullable=False)
    price_yatra_child = db.Column(db.Integer, nullable=False)
    # price_2_day = db.Column(db.Integer, nullable=False)

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
    area_leader = db.Column(db.String, nullable=False)


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_area = db.Column(db.String, nullable=False)
    area_leader = db.Column(db.String, nullable=False)
    user_mobile = db.Column(db.String, nullable=False)
    user_email = db.Column(db.String, nullable=False)
    date_time = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    room_type = db.Column(db.String, nullable=False)
    # room_category=db.Column(db.String, nullable=False)
    booking_type = db.Column(db.String, nullable=False)
    person_count = db.Column(db.Integer, nullable=False)
    child_count = db.Column(db.Integer, nullable=False)
    # yatra_days = db.Column(db.String, nullable=False)
    total_payable = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Integer, nullable=False)
    amount_pending = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.String)
    utr_receipt_number = db.Column(db.String, nullable=False)
    amount_2 = db.Column(db.Integer)
    utr_2 = db.Column(db.String)
    trn_dt_2 = db.Column(db.String)
    amount_3 = db.Column(db.Integer)
    utr_3 = db.Column(db.String)
    trn_dt_3 = db.Column(db.String)
    status = db.Column(db.String)
    cancellation_date = db.Column(db.String)
    room_no = db.Column(db.String)


db.create_all()

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

class CategoryChoices():
    def __init__(self):
        pass
    def hotel_name(self):
        hotel_names = []
        names = db.session.query(CategoryList.name).distinct()
        for name in names:
            hotel_names.append(name.name)
        return(hotel_names)
    def hotel_description(hotel):
        descriptions = []
        desc = CategoryList.query.filter_by(name=hotel).all()
        for des in desc:
            descriptions.append(des.description)
        return (descriptions)

    def room_availability(hotel, description):
        total_rooms = CategoryList.query.filter_by(name=hotel, description=description).first()
        return total_rooms

class DoBookingHotelForm(FlaskForm):
    hotel_name = SelectField("Choose Category", choices=CategoryChoices.hotel_name(self=""), validators=[DataRequired()])
    submit = SubmitField("Select Category")

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
            area_leader=form.area_leader.data,
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
    if form.validate_on_submit():
        print('hi')

        global name_of_hotel
        global naklank1_double_bed_max_count

        if len(name_of_hotel) == 0:
            x=0
            name_of_hotel = form.hotel_name.data

            hotel_detail = CategoryList.query.filter_by(name=name_of_hotel).all()
            choices = [(hotel.description, hotel.name) for hotel in hotel_detail]
            return render_template("do_booking.html", hotel=name_of_hotel, form=form, choices=choices, logged_in=current_user.is_authenticated, current_user=current_user, x=x)

    if len(name_of_hotel) != 0:
        print('yy')
        x=1
        room_desc = request.form.get("description")
        category_name = request.form.get("category")
        hotel_name = request.form.get("hotel")
        # yatra_days = request.form.get("yatra_days")
        type_of_room = request.form.get("type_of_room")
        hotel_detail = CategoryList.query.filter_by(name=hotel_name, description=room_desc).first()


        hotel_detail = CategoryList.query.filter_by(name=hotel_name, description=room_desc).first()

        # if not hotel_detail:
        #     flash("Invalid hotel selection. Please select a hotel again.", "error")
        #     return render_template("do_booking.html", form=form, logged_in=current_user.is_authenticated,
        #                            current_user=current_user, x=x)

        type_of_room_dorm = request.form.get('type_of_room_dorm')

        if type_of_room_dorm:
            # Handle dormitory booking
            type_of_room = type_of_room_dorm
        else:
            type_of_room = request.form.get("type_of_room")

        # Get the selected person count
        person_count_dormitory = request.form.get('person_count_dormitory')
        person_count_3 = request.form.get('person_count')  # Assuming this dropdown is for 3 bed
        person_count_2 = request.form.get('person_count_2')  # Assuming this dropdown is for 2 bed
        person_count_4 = request.form.get('person_count_4') # Assuming this dropdown is for 4 bed
        bed_count = request.form.get('bed_count')  # Assuming this dropdown is for individual beds, then it is taking count of bed

        # Handle which person count was selected
        if person_count_dormitory:
            person_count = int(person_count_dormitory)
        elif person_count_3:
            person_count = int(person_count_3)
        elif person_count_2:
            person_count = int(person_count_2)
        elif person_count_4:
            person_count = int(person_count_4)
        elif bed_count:
            person_count = int(bed_count)
        else:
            person_count = 0  # Handle the case where no person count is selected

        child_count = request.form.get('child_count')

        name_of_hotel = ""
        print(f'person count is {person_count}')

        # calculating discount
        discount_cut_off_date = datetime(2025, 2, 16).date()
        discount_cut_off_date_second = datetime(2025, 2, 23).date()
        current_date = datetime.now().date()

        if current_date <= discount_cut_off_date:
            discount = 200 * int(person_count)
        elif current_date <= discount_cut_off_date_second:
            discount = 100 * int(person_count)
        else:
            discount = 0

        # calculating total laxmi payable
        # if yatra_days == '3day':
        #     per_person_charge = hotel_detail.price_3_day
        # elif yatra_days == '2day_8_9' or yatra_days == '2day_9_10':
        #     per_person_charge = hotel_detail.price_2_day
        # else:
        #     per_person_charge = 0
        per_person_charge = hotel_detail.price_yatra

        if hotel_detail and hotel_detail.booked is not None:
            total_laxmi = (int(person_count) * int(per_person_charge)) + (int(child_count) * int(children_charges)) - int(discount)
            # rooms_available = hotel_detail.quantity - hotel_detail.booked + hotel_detail.cancelled

            # if (type_of_room=='complete_room' and rooms_available>=1) or (type_of_room=='dorm_matajis' and rooms_available>=person_count) or (type_of_room=='dorm_prjis' and rooms_available>=person_count) or (type_of_room=='bed_prjis' and room_desc=='2 bed' and rooms_available>=(person_count/2)) or (type_of_room=='bed_matajis' and room_desc=='2 bed' and rooms_available>=(person_count/2)) or (type_of_room=='bed_prjis' and room_desc=='3 bed' and rooms_available>=(person_count * 0.33)) or (type_of_room=='bed_matajis' and room_desc=='3 bed' and rooms_available>=(person_count * 0.33)) or (type_of_room=='bed_prjis' and room_desc=='4 bed' and rooms_available>=(person_count/4)) or (type_of_room=='bed_matajis' and room_desc=='4 bed' and rooms_available>=(person_count/4)):
            # # if rooms_available > 0.1:
            return render_template("do_booking.html", hotel=hotel_name, form=form, description=room_desc, hotel_detail=hotel_detail, type_of_room=type_of_room, logged_in=current_user.is_authenticated, current_user=current_user, x=x,
                                       person_count=person_count, child_count=child_count, discount=discount,
                                       per_person_charge=per_person_charge, total_laxmi=total_laxmi)
            # else:
            #     if type_of_room == 'dorm_matajis' or type_of_room == 'dorm_prjis':
            #         message = f"Booking cannot be made as {rooms_available:.2f} bed(s) available"
            #     else:
            #         message = f"Booking cannot be made as {rooms_available:.2f} room(s) available"
            #     return render_template("do_booking.html", hotel=hotel_name, form=form, description=room_desc, message=message, type_of_room=type_of_room, logged_in=current_user.is_authenticated, current_user=current_user, x=x)
        else:
            return render_template("do_booking.html", form=form, logged_in=current_user.is_authenticated,
                                   current_user=current_user, x=x)

    return render_template("do_booking.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route('/forgot_password', methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if request.method == 'GET':

        return render_template("forgot_password.html", form=form, logged_in=current_user.is_authenticated,
                               current_user=current_user)

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('forgot_password'))
        else:
            flash("Password has been reset and shared on the email. "
                  "If, it's not in Inbox, then check your spam folder.")
            alphabet = string.ascii_letters + string.digits
            new_password = ''.join(secrets.choice(alphabet) for _ in range(6))
            print(new_password)
            print(user.name)
            hash_and_salted_password = generate_password_hash(
                new_password,
                method='pbkdf2:sha256',
                salt_length=12
            )
            user.password = hash_and_salted_password
            db.session.commit()

            recipient_email = email
            subject = "SP-3C - Password Reset"
            body = f"Your password has been reset. Your new password is <strong>{new_password}</strong>."
            # Create the MIMEText object with HTML content
            html_message = MIMEText(body, "html")

            # Create the MIMEMultipart object and set the sender, recipient, subject, and attach the HTML content
            message = MIMEMultipart()
            message["From"] = email_address
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(html_message)

            # Establish a connection with the SMTP server (in this case, Gmail's SMTP server)
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Enable TLS
                server.login(email_address, email_password)

                # Send the email
                server.sendmail(email_address, recipient_email, message.as_string())

            return render_template("message.html", heading="Forgot Password",
                                logged_in=current_user.is_authenticated, msg="",
                                current_user=current_user)


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
            area_leader = request.form.get("area_leader"),
            date_time=current_date_time,
            category=request.form.get("hotel"),
            room_type=request.form.get("description"),
            # room_category=request.form.get("room_category"),
            booking_type=request.form.get("booking_type"),
            person_count=int(request.form.get("person_count")),
            child_count=int(request.form.get("child_count")),
            # yatra_days=request.form.get("yatra_days"),
            total_payable=int(request.form.get("total_laxmi")),
            discount=int(request.form.get("discount")),
            amount_paid=int(request.form.get("amount_paid")),
            amount_pending=int((int(request.form.get("total_laxmi")) - int(request.form.get("amount_paid")))),
            transaction_date=request.form.get("transaction_date"),
            utr_receipt_number=request.form.get("utr"),
            status='Booked',
        )
        db.session.add(new_booking)
        db.session.commit() #adding data in booking list

        hotel_list = CategoryList.query.filter_by(name=request.form.get("hotel"), description=request.form.get("description")).first()

        if request.form.get("booking_type") == 'complete_room':
            hotel_list.booked += 1
        elif request.form.get("booking_type") == 'dorm_matajis' or request.form.get("booking_type") == 'dorm_prjis':
            hotel_list.booked += int(request.form.get("person_count"))
        else: #in case of bed_prjis / bed_matajis
            if request.form.get("description") == '2 bed':
                hotel_list.booked += (int(request.form.get("person_count"))/2)
            elif request.form.get("description") == '4 bed': # type_of_room is '4 bed'
                hotel_list.booked += (int(request.form.get("person_count")) / 4)
            else: # type_of_room is '3 bed'
                hotel_list.booked += (int(request.form.get("person_count")) / 3)

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

            updated_booking.amount_2 = request.form.get("amount_2")
            updated_booking.trn_dt_2 = request.form.get("trn_dt_2")
            updated_booking.utr_2 = request.form.get("utr_2")

            updated_booking.amount_3 = request.form.get("amount_3")
            updated_booking.trn_dt_3 = request.form.get("trn_dt_3")
            updated_booking.utr_3 = request.form.get("utr_3")
            updated_booking.amount_pending = int(updated_booking.total_payable) - int(request.form.get("amount_paid")) - int(request.form.get("amount_2")) - int(request.form.get("amount_3"))

            db.session.commit()

            my_bookings = Booking.query.filter_by(user_id=current_user.id).all()

            return render_template("review_booking.html", bookings=my_bookings, logged_in=current_user.is_authenticated,
                                   current_user=current_user)
    else:
        return render_template("index.html", logged_in=current_user.is_authenticated, current_user=current_user)

@app.route('/additional_payment', methods=["GET", "POST"])
def additional_payment():

    if request.method == 'POST':
        if request.form.get("form_purpose") == "display_pymnt_form":
            booking_addtnl_pymnt = Booking.query.filter_by(id=request.form.get("booking_id")).first()

            return render_template("additional_payment.html", booking=booking_addtnl_pymnt, logged_in=current_user.is_authenticated, current_user=current_user)

        elif request.form.get("form_purpose") == "update_payment":
            updated_booking = Booking.query.filter_by(id=request.form.get("booking_id")).first()
            if not updated_booking.amount_2:
                updated_booking.amount_2 = request.form.get("extra_amount")
                updated_booking.trn_dt_2 = request.form.get("payment_date")
                updated_booking.utr_2 = request.form.get("utr_detail")
                updated_booking.amount_pending -= int(request.form.get("extra_amount"))
                print('2')
                db.session.commit()
            elif not updated_booking.amount_3:
                updated_booking.amount_3 = request.form.get("extra_amount")
                updated_booking.trn_dt_3 = request.form.get("payment_date")
                updated_booking.utr_3 = request.form.get("utr_detail")
                updated_booking.amount_pending -= int(request.form.get("extra_amount"))
                print('3')
                db.session.commit()
            else:
                message = "Error! You have made large number of payments for this Booking ID. Please contact Yatra Incharge for updating further payments."

                return render_template("additional_payment.html", booking=updated_booking,
                                       logged_in=current_user.is_authenticated, current_user=current_user, message=message)

            message = "Success! You have successfully updated the payment detail."
            my_bookings = Booking.query.filter_by(user_id=current_user.id).all()

            return render_template("review_booking.html", bookings=my_bookings, logged_in=current_user.is_authenticated,
                                   current_user=current_user, message=message)
    else:
        return render_template("index.html", logged_in=current_user.is_authenticated, current_user=current_user)


@app.route('/cancel_booking', methods=["GET", "POST"])
def cancel_booking():
    if request.method == 'POST':
        cancelled_date_time = datetime.now()

        cancelled_booking = Booking.query.filter_by(id=request.form.get("booking_id")).first()
        cancelled_booking.status = "Cancelled"
        cancelled_booking.cancellation_date = cancelled_date_time

        category_cancld = cancelled_booking.category
        room_type_cancld = cancelled_booking.room_type
        # room_category_cancld = cancelled_booking.room_category
        booking_type_cancld = cancelled_booking.booking_type
        person_count_cancld = cancelled_booking.person_count
        db.session.commit() #updating the booking status as Cancelled

        category_list = CategoryList.query.filter_by(name=category_cancld,
                                                  description=room_type_cancld).first()

        if booking_type_cancld == 'complete_room':
            category_list.cancelled += 1
        elif booking_type_cancld == 'dorm_matajis' or booking_type_cancld == 'dorm_prjis':
            category_list.cancelled += int(person_count_cancld)
        else:  # in case of bed_prjis / bed_matajis
            if room_type_cancld == '2 bed':
                category_list.cancelled += (int(person_count_cancld) / 2)
            elif room_type_cancld == '4 bed':  # type_of_room is '4 bed'
                category_list.cancelled += (int(person_count_cancld) / 4)
            else:  # type_of_room is '3 bed'
                category_list.cancelled += (int(person_count_cancld) / 3)

        db.session.commit()  # Update the cancelled rooms in the hotel list


        # Fetch the bookings for the current user
        my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
        return render_template("review_booking.html", bookings=my_bookings, logged_in=current_user.is_authenticated, current_user=current_user)

    else:
        return render_template("index.html", logged_in=current_user.is_authenticated, current_user=current_user)

# @app.route('/verify_booking', methods=["GET", "POST"])
# @account_only
# def verify_booking():
#     current_date_time = datetime.now()
#
#     if request.method == "POST":
#         verified_post = Booking.query.filter_by(id=request.form.get("booking_id")).first()
#         verified_post.status = "Verified"
#         verified_post.verification_date = current_date_time
#         db.session.commit()
#     to_be_verified = Booking.query.filter_by(status="To be verified").all()
#     return render_template("verify_booking.html", bookings_tbv=to_be_verified, logged_in=current_user.is_authenticated, current_user=current_user)

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
    form = AddCategoryForm()
    if form.validate_on_submit():
        new_hotel = CategoryList(
            name=form.name.data,
            description=form.description.data,
            # category=form.category.data,
            # quantity=form.quantity.data,
            booked=form.booked.data,
            cancelled=form.cancelled.data,
            price_yatra=form.price_yatra.data,
            price_yatra_child=form.price_yatra_child.data,
            # price_2_day=form.price_2_day.data,
            # occupancy=form.occupancy.data,
            # occupancy1=form.occupancy1.data,
            # occupancy2=form.occupancy2.data,
        )
        db.session.add(new_hotel)
        db.session.commit()
        return redirect(url_for("hotel_details"))
    return render_template("add_hotel.html", form=form, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route("/hotel", methods=['GET', 'POST'])
def hotel_details():
    # selected_category = request.form.get('category')  # Get selected category from form

    # Fetch all distinct room categories from the database
    # room_categories = db.session.query(CategoryList.category).distinct().all()

    # Fetch hotels based on the selected category, or all hotels if no category is selected
    # if selected_category:
    #     hotels = CategoryList.query.filter_by(category=selected_category).all()
    # else:
    categories = CategoryList.query.all()
    return render_template("hotels.html", categories=categories, logged_in=current_user.is_authenticated, current_user=current_user)

@app.route("/update_hotel_details", methods=['GET', 'POST'])
def update_hotel_details():
    if request.method == 'POST':

        if request.form.get("form_purpose") == "passing_id_for_update":
            update_category = CategoryList.query.filter_by(id=request.form.get("category_id")).first()
            return render_template("update_hotel_details.html", category=update_category,
                                   logged_in=current_user.is_authenticated, current_user=current_user)

        elif request.form.get("form_purpose") == "update_hotel_details":
            updated_category = CategoryList.query.filter_by(id=request.form.get("category_id")).first()
            # updated_category.category = request.form.get("category")
            # updated_category.quantity = request.form.get("quantity")
            updated_category.booked = request.form.get("booked")
            updated_category.cancelled = request.form.get("cancelled")
            updated_category.price_yatra = request.form.get("price_yatra")
            # updated_category.price_2_day = request.form.get("price_2_day")
            db.session.commit()

            return redirect(url_for('hotel_details'))

    return redirect(url_for('hotel_details'))


@app.route('/download_data_excel')
def download_data_excel():
    bookings = Booking.query.all()

    # Create a CSV buffer to write data
    output = io.StringIO()
    writer = csv.writer(output)

    # Write column headings
    writer.writerow([
        'Booking ID', 'Status','User', 'Area', 'Area Leader', 'Mobile',
        'Email', 'Date', 'Room Category','Room Type', 'Booking Type',
        'Total Persons', 'Children', 'Amt Payable',
        'Discount Given', 'Amt Paid', 'Transaction Dt',
        'UTR Receipt No.', 'Amt 2', 'Trsctn Dt 2','UTR 2', 'Amt 3', 'Trsctn Dt 3',
        'UTR 3', 'Amt Pending', 'Cancellation Date', 'Room No'
    ])

    # Write data rows
    for booking in bookings:
        writer.writerow([
            booking.id, booking.status, booking.user_name, booking.user_area, booking.area_leader,
            booking.user_mobile, booking.user_email, booking.date_time,
            booking.category, booking.room_type, booking.booking_type,
            booking.person_count, booking.child_count,
            booking.total_payable, booking.discount, booking.amount_paid,
            booking.transaction_date, booking.utr_receipt_number,
            booking.amount_2, booking.trn_dt_2, booking.utr_2, booking.amount_3, booking.trn_dt_3,
            booking.utr_3, booking.amount_pending, booking.cancellation_date, booking.room_no
        ])

    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=bookings.csv"
    response.headers["Content-type"] = "text/csv"

    return response
    
@app.route('/download_hotel_booking_status')
def download_hotel_booking_status():
    hotels = CategoryList.query.all()

    # Create a CSV buffer to write data
    output = io.StringIO()
    writer = csv.writer(output)

    # Write column headings
    writer.writerow([
        'Hotel ID', 'Name', 'Description', 'Category', 'Quantity', 'Booked', 'Cancelled',
        'Yatra Price (3 day)', 'Yatra Price (2 day)'
    ])

    # Write data rows
    for hotel in hotels:
        writer.writerow([
            hotel.id, hotel.name, hotel.description, hotel.category,
            hotel.quantity, hotel.booked, hotel.cancelled, hotel.price_yatra,
            hotel.price_2_day,
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
