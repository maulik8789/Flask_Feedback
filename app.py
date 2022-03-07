from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/users/<string:username>', methods=['GET', 'POST'])
def show_secret(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    
    user_form = UserForm()
    user_username = User.query.get(username)
    # user_email = User.query.get(email)
    # user_first_name = User.query.get(first_name)
    # user_last_name = User.query.get(last_name)
    
    form = FeedbackForm()
    all_feedbacks = Feedback.query.all()
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title = title,content=content, username=session['username'])
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback Created!', 'success')
        return redirect(f'/users/{username}')
        
    return render_template("feedback.html", form=form, all_feedbacks=all_feedbacks, user_form = user_form)


@app.route('/users/<string:username>', methods=["POST"])
def delete_tweet(username):
    """Delete tweet"""
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(id)
    if feedback.user.username == session['username']:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", "info")
        return redirect(f'/users/{feedback.user.username}')

    flash("You don't have permission to do that!", "danger")
    return redirect(f'/users/{feedback.user.username}')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, first_name, last_name, email)

        db.session.add(new_user)
        # try:
        db.session.commit()
        # except IntegrityError:
            # form.username.errors.append('Username taken.  Please pick another')
            # return render_template('register.html', form=form)
        # session['user_id'] = new_user.id
        session['username'] = new_user.username

        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f'/users/{username}')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = user.username
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')
