from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, DeleteForm, FeedbackForm
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

   if "username" in session:
      flash(f"{session['username']} Already Logged In!")
      return redirect(f"/users/{session['username']}")

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
      return redirect(f"/users/{user.username}")

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
   
   if "username" in session:
      flash(f"{session['username']} Already Logged In!")
      return redirect(f"/users/{session['username']}")

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
         return redirect(f"/users/{user.username}")

      else:
         form.username.errors = ["Bad name/password"]

   return render_template("users/login.html", form=form)


# GET /secret
# Return the text “You made it!” (don’t worry, we’ll get rid of this soon)
# @app.route('/secret')
# def secret_page():

#    return "You made it!"

# Now that we have some logging in and and logging out working. Let’s add some authorization! When a user logs in, take them to the following route:

# GET /users/<username>
# Display a template the shows information about that user (everything except for their password)

# You should ensure that only logged in users can access this page.
@app.route('/users/<username>')
def show_user(username):
   """Direct to User page and populate with current user information."""

   if "username" not in session or username != session['username']:
      return redirect(f"/users/{session['username']}")

   user = User.query.get(username)
   form = DeleteForm()

   return render_template("users/show.html", user=user, form=form)



# GET /logout
# Clear any information from the session and redirect to /
@app.route('/logout')
def logout_user():
   """Log current user out of session."""

   flash("Logged Out!")
   session.pop('username')
   return redirect("/")


# POST /users/<username>/delete
# Remove the user from the database and make sure to also delete all of their feedback. 
# Clear any user information in the session and redirect to /. 
# Make sure that only the user who is logged in can successfully delete their account
@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
   """Delete User"""


   return redirect("/login")


# GET /users/<username>/feedback/add
# Display a form to add feedback Make sure that only the user who is logged in can see this form
# POST /users/<username>/feedback/add
# Add a new piece of feedback and redirect to /users/<username> — Make sure that only the user who is logged in can successfully add feedback
@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
   """Add Feedback"""

   if "username" not in session:
      flash("Please login first!")
      return redirect("/")
   
   form = FeedbackForm()

   if form.validate_on_submit():
      title = form.title.data
      content = form.content.data

      new_feedback = Feedback(title=title, content=content, username=username)

      db.session.add(new_feedback)
      db.session.commit()

      return redirect(f"/users/{username}")
   else:
      return render_template("feedback/new.html", form=form)


# GET /feedback/<feedback-id>/update
# Display a form to edit feedback — **Make sure that only the user who has written that feedback can see this form **
# POST /feedback/<feedback-id>/update
# Update a specific piece of feedback and redirect to /users/<username> — Make sure that only the user who has written that feedback can update it
@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
   """Update Feedback"""

   if "username" not in session:
      flash("Please login first!")
      return redirect("/")
   
   feedback = Feedback.query.get_or_404(feedback_id)

   form = FeedbackForm(obj=feedback)

   if form.validate_on_submit():
      feedback.title = form.title.data
      feedback.content = form.content.data

      db.session.commit()

      return redirect(f"/users/{feedback.username}")


   return render_template("/feedback/edit.html", form=form, feedback=feedback)


# POST /feedback/<feedback-id>/delete
# Delete a specific piece of feedback and redirect to /users/<username> — Make sure that only the user who has written that feedback can delete it
@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
   """Delete Feedback"""
   
   if "username" not in session:
      flash("Please login first!")
      return redirect("/")
   
   feedback = Feedback.query.get_or_404(feedback_id)
   
   form = DeleteForm()

   if form.validate_on_submit():
      db.session.delete(feedback)
      db.session.commit()

   flash(f"Feedback '{feedback.title}' Deleted!")

   return redirect(f"/users/{feedback.username}")