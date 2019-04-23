from flask import Flask, jsonify, request, render_template, session, redirect, flash
from models import User, connect_db, db
from forms import CreateUser, LoginUser
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

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/secret')

    else:
        return render_template('userform.html', form=form)


@app.route("/secret")
def secret():
    """Example hidden page for logged-in users only."""

    if "user_id" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

        # alternatively, can return HTTP Unauthorized status:
        #
        # from werkzeug.exceptions import Unauthorized
        # raise Unauthorized()

    else:
        return render_template("secret.html")


@app.route('/login', methods=["GET", "POST"])
def login_form():
    form = LoginUser()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session["user_id"] = user.id  # keep logged in
            return redirect("/secret")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("loginform.html", form=form)

@app.route('/logout')
def logout():
    # clear the session then redirect to home
    """Logs user out and redirects to homepage."""

    session.pop("user_id")
    flash("You've been logged out")
    return redirect("/login")