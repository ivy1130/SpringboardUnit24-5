from crypt import methods
from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import ForeignKeyConstraint
from models import connect_db, db, User, Feedback
from forms import CreateUserForm, LoginUserForm, AddOrUpdateFeedbackForm
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "odsgodfgjdfg"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def index():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register_user.html', form=form)
        
        session['user'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")

        return redirect(f'/users/{new_user.username}')

    return render_template('register_user.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    form = LoginUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome Back, {user.username}!", "success")
            session['user'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login_user.html', form=form)

@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop('user')
    flash("Goodbye!", "info")
    return redirect('/')

@app.route('/users/<username>')
def show_user_details(username):
    if "user" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')

    user = User.query.get_or_404(username)

    return render_template('user_details.html', user=user, feedbacks=user.feedbacks)

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    if "user" not in session:
        flash("You must log in first!", "danger")
        return redirect('/login')

    elif username != session['user']:
        flash("You can only add feedback to your own profile!", "danger")
        return redirect(f'/users/{session["user"]}')

    else:
        form = AddOrUpdateFeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            username = username

            new_feedback = Feedback.add_feedback(title, content, username)
            db.session.add(new_feedback)
            db.session.commit()

            return redirect(f'/users/{username}')
    
        return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    if "user" not in session:
        flash("You must log in first!", "danger")
        return redirect('/login')

    elif feedback.username != session['user']:
        flash("You can only update your own feedback", "danger")
        return redirect(f'/users/{session["user"]}')

    else:
        form = AddOrUpdateFeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()

            return redirect(f'/users/{feedback.username}')

        return render_template('update_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    if "user" not in session:
        flash("You must log in first!", "danger")
        return redirect('/login')

    elif feedback.username != session['user']:
        flash("You can only delete your own feedback", "danger")
        return redirect(f'/users/{session["user"]}')

    else:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", "info")

        return redirect(f'/users/{feedback.username}')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    user = User.query.get_or_404(username)

    if "user" not in session:
        flash("You must log in first!", "danger")
        return redirect('/login')

    elif user.username != session['user']:
        flash("You can only delete your own account", "danger")
        return redirect(f'/users/{session["user"]}')

    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} deleted!", "info")

        return redirect('/')