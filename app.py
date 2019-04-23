from flask import Flask, jsonify, request, render_template, session, redirect, flash
from models import User, connect_db, db, Feedback
from forms import CreateUser, LoginUser, FeedbackForm
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from secret import app_secret


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flaskFeedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
bcrypt = Bcrypt()

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = app_secret

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route('/')
def redirect_to_user():
    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def add_user():
    form = CreateUser()

    ##if email or username exist then redirect and flash
    username = form.username.data
    email = form.email.data

    USER_EXIST = User.query.filter_by(username=username).first() != None
    EMAIL_EXIST = User.query.filter_by(email=email).first() != None 

    if USER_EXIST or EMAIL_EXIST:
        flash("Username or Email Already Exists!")
        return render_template('userform.html', form=form)

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id  # keep logged in

        return redirect(f'/users/{username}')

    else:
        return render_template('userform.html', form=form)


@app.route("/users/<username>")
def secret(username):
    """Example hidden page for logged-in users only."""

    user = User.query.filter_by(username=username).first()

    if "user_id" not in session or session["user_id"] != user.id:
        flash("You must be logged in to view!")
        return redirect("/login")

        # alternatively, can return HTTP Unauthorized status:
        #
        # from werkzeug.exceptions import Unauthorized
        # raise Unauthorized()

    else:

        # #get information about the user (minus the password)
        user = User.query.filter_by(username=username).first()
        feedbacks = user.feedbacks

        return render_template("secret.html", user=user, feedbacks=feedbacks)


@app.route('/login', methods=["GET", "POST"])
def login_form():
    form = LoginUser()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session["user_id"] = user.id  # keep logged in
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("loginform.html", form=form)

@app.route('/logout')
def logout():
    # clear the session then redirect to home
    """Logs user out and redirects to homepage."""

    if session.get('user_id'):
        session.pop("user_id")
        flash("You've been logged out")

    return redirect("/login")

@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    # get current user
    user = User.query.filter_by(username=username).first()

    if "user_id" not in session and session["user_id"] == user.id:
        flash("You must be logged in to view!")
        return redirect("/login")

    # alternatively, can return HTTP Unauthorized status:
    #
    # from werkzeug.exceptions import Unauthorized
    # raise Unauthorized()

    else:
        # remove from db
        db.session.delete(user)
        db.session.commit()
        session.pop("user_id")
        flash("User deleted")
        return redirect("/register")

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feed_back(username):

    form = FeedbackForm()

    ##if user is not logged in, flash message and redirect
    user = User.query.filter_by(username=username).first()

    USER_NOT_LOGGED_IN = "user_id" not in session
    NOT_SAME_USER = session.get('user_id') != user.id

    
    if USER_NOT_LOGGED_IN or NOT_SAME_USER:
        flash("Please Login to Submit Feedback!")
        return redirect("/login")

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_fb = Feedback(title=title,content=content,username=username)
        db.session.add(new_fb)
        db.session.commit()

        return redirect(f'/users/{username}')

    else:
        return render_template('feedbackForm.html', form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feed_back(feedback_id):


    feedback = Feedback.query.get(feedback_id)
    username = feedback.username

    ##if user is not logged in, flash message and redirect
    user = User.query.filter_by(username=username).first()

    USER_NOT_LOGGED_IN = "user_id" not in session
    NOT_SAME_USER = session.get('user_id') != user.id

    if USER_NOT_LOGGED_IN or NOT_SAME_USER:
        flash("Please Login to Submit Feedback!")
        return redirect("/login")

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback.title = title
        feedback.content = content

        db.session.commit()

        return redirect(f'/users/{username}')

    else:
        return render_template('feedbackForm.html', form=form)


@app.route("/feedback/<int:feedback_id>/delete", methods=['POST'])
def delete_feedback(feedback_id):
    # get current user
    feedback = Feedback.query.get(feedback_id)
    username = feedback.username

    user = User.query.filter_by(username=username).first()

    if "user_id" not in session and session["user_id"] == user.id:
        flash("You must be logged in to view!")
        return redirect("/login")

    # alternatively, can return HTTP Unauthorized status:
    #
    # from werkzeug.exceptions import Unauthorized
    # raise Unauthorized()

    else:
        # remove from db
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted")
        return redirect(f"/users/{username}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('404.html')