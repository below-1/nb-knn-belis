from functools import wraps
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)
from serafim.model import db_session_required
from serafim.model import User

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

@auth_blueprint.route('/login_admin', methods=['GET', 'POST'])
@db_session_required
def login_admin():
    if request.method == 'GET':
        return render_template("auth/login_admin.html")
    form = request.form
    username = form['username']
    password = form['password']

    db_session = g.get('db_session')
    error = None
    user = db_session.query(User).filter(User.username == username).first()

    if user is None:
        error = 'Incorrect username'
    elif not check_password_hash(user.password, password):
        error = 'Incorrect password'

    if error is None:
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return redirect(url_for('admin.admin_list_dataset'))

    flash(error)
    return redirect(url_for('auth.login_admin'))

@auth_blueprint.route('/signup_user', methods=['GET', 'POST'])
@db_session_required
def signup_user():
    if request.method == 'GET':
        return render_template('user/signup.html')
    form = request.form
    username = form['username']
    password = form['password']
    db_session = g.get('db_session')
    user = User(username=username, nama=username, password=generate_password_hash(password), role='user')
    db_session.add(user)
    db_session.commit()
    return redirect(url_for('auth.user_login'))

@auth_blueprint.route('/login_user', methods=['GET', 'POST'])
@db_session_required
def login_user():
    if request.method == 'GET':
        return render_template("user/login.html")
    form = request.form
    username = form['username']
    password = form['password']

    db_session = g.get('db_session')
    error = None
    user = db_session.query(User).filter(User.username == username).filter(User.role == 'user').first()

    if user is None:
        error = 'Incorrect username'
    elif not check_password_hash(user.password, password):
        error = 'Incorrect password'

    if error is None:
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return redirect(url_for('user.user_prediksi_form'))

    flash(error)
    return redirect(url_for('auth.login_user'))


@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_admin'))

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_admin'))
        return f(*args, **kwargs)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_admin'))
        if ('role' not in session) or (session['role'] != 'admin'):
            return redirect(url_for('auth.login_admin'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_user'))
        if ('role' not in session) or (session['role'] != 'user'):
            return redirect(url_for('auth.login_user'))
        return f(*args, **kwargs)
    return decorated_function