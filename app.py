from flask import (Flask, g, render_template, flash, redirect, url_for,
                    abort)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                            login_required, current_user)

from slugify import slugify
import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = "mansd;ofq98wm[ieod; kva'we-#]"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect(reuse_if_open=True)
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Create a user."""
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        models.User.create_user(
            username=form.username.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash("Your username or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your username or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out!", "success")
    return redirect(url_for('index'))


@app.route('/new_entry', methods=('GET', 'POST'))
@login_required
def entry():
    """Create a new entry."""
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Entry.create(user=g.user._get_current_object(),
                            title=form.title.data,
                            timestamp=form.timestamp.data,
                            time_spent=form.time_spent.data,
                            content=form.content.data.strip(),
                            resources=form.resources.data.strip())
        flash("Entry created! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('new_entry.html', form=form)


@app.route('/edit/<slug>', methods=('GET', 'POST'))
@login_required
def edit(slug):
    """Edit an entry."""
    try:
        entry = models.Entry.get(models.Entry.slug == slug)
    except models.DoesNotExist:
        abort(404)
    else:
        form = forms.EditEntryForm(obj=entry)
        if form.validate_on_submit():
            models.Entry.update(
                title = form.title.data,
                slug = slugify(form.title.data),
                timestamp = form.timestamp.data,
                time_spent = form.time_spent.data,
                content = form.content.data.strip(),
                resources = form.resources.data.strip()
            ).where(models.Entry.slug == entry.slug).execute()
            flash("Entry updated!", "success")
            return redirect(url_for('index'))
        return render_template('edit.html', form=form)


@app.route('/entries')
@login_required
def entries():
    """View all entries."""
    entries = models.Entry.select().order_by(-models.Entry.timestamp)
    if entries.count() == 0:
        abort(404)
    else:
        return render_template('entries.html', entries=entries)


@app.route('/details/<slug>')
@login_required
def details(slug):
    """View entry's detail."""
    try:
        entry = models.Entry.get(models.Entry.slug == slug)
    except models.DoesNotExist:
        abort(404)
    return render_template('details.html', entry=entry)


@app.route('/delete/<slug>')
@login_required
def delete(slug):
    """Delete an entry."""
    try:
        entry = models.Entry.get(models.Entry.slug == slug)
    except models.DoesNotExist:
        abort(404)
    else:
        entry.delete_instance()
        flash("Entry deleted!", "success")
        return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()
    models.User.create_user(
        username="yasuko",
        password="password",
        admin=True
    )
    app.run(debug=DEBUG, host=HOST, port=PORT)
