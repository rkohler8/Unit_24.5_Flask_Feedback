from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


# GET /
# Redirect to /register.
@app.route('/')
def home_page():

   return redirect('/register')


# GET /register
# Show a form that when submitted will register/create a user. This form should accept a username, password, email, first_name, and last_name.

# Make sure you are using WTForms and that your password input hides the characters that the user is typing!
# POST /register
# Process the registration form by adding a new user. Then redirect to /secret
@app.route('/register', methods=["GET", "POST"])
def register():
   """Register user: produce form & handle form submission."""

   form = RegisterForm()

   if form.validate_on_submit():
      username = form.username.data
      pwd = form.password.data
      email = form.email.data
      first_name = form.first_name.data
      last_name = form.last_name.data

      user = User.register(username, 
                           pwd, 
                           email, 
                           first_name, 
                           last_name)
      db.session.add(user)
      db.session.commit()

      session["username"] = user.username

      # on successful login, redirect to secret page
      return redirect("/secret")

   else:
      return render_template("users/register.html", form=form)


# GET /login
# Show a form that when submitted will login a user. This form should accept a username and a password.

# Make sure you are using WTForms and that your password input hides the characters that the user is typing!
   # POST /login
# Process the login form, ensuring the user is authenticated and going to /secret if so.
@app.route('/login', methods=["GET", "POST"])
def login():
   """Produce login form or handle login."""

   form = LoginForm()
   # return redirect("/secret")


   if form.validate_on_submit():
      username = form.username.data
      pwd = form.password.data

      # authenticate will return a user or False
      user = User.authenticate(username, pwd)

      if user:
         flash(f"Welcome Back, {user.username}!")
         session["username"] = user.username  # keep logged in
         return redirect("/secret")

      else:
         form.username.errors = ["Bad name/password"]

   return render_template("users/login.html", form=form)


# GET /secret
# Return the text “You made it!” (don’t worry, we’ll get rid of this soon)
@app.route('/secret')
def secret_page():

   return "You made it!"




# GET /logout
# Clear any information from the session and redirect to /
@app.route('/logout')
def logout_user():
   """Log current user out of session"""

   flash("Logged Out!")
   session.pop('username')
   return redirect('/')