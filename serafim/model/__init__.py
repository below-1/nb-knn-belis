from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
import click

from serafim.config import DATABASE_URI
from serafim.model.base import Base
from serafim.model.User import User
from serafim.model.ThreeLevelEnum import ThreeLevelEnum
from serafim.model.DsetRow import DsetRow
from serafim.model.DsetRow import TingkatPendidikan
from serafim.model.DsetRow import StatusAdat
from serafim.model.DsetRow import Pekerjaan
from serafim.model.DsetRow import TingkatEkonomi
from serafim.model import converter
from serafim.model.seed import seed

_engine = create_engine(DATABASE_URI)
_DbSession = sessionmaker(autoflush=True)

def _create_session():
    db_session = _DbSession(bind=_engine)
    return db_session

@click.command('init-db')
@with_appcontext
def init_db():
    print(DATABASE_URI)
    print(Base.metadata.create_all(_engine))
    dbsession = _create_session()
    phash = generate_password_hash('super-admin')
    admin = User(
        nama='Super admin',
        username='super-admin',
        role='super-admin',
        password=phash
    )
    dbsession.add(admin)
    dbsession.commit()

# Set up seeding
@click.command('seed-db')
@with_appcontext
def do_seed():
    dbsession = _create_session()
    user_id = 1
    filename = "serafim/data.csv"
    seed(session=dbsession, user_id=user_id, filename=filename)

# For lack of understanding of testing
@click.command('test-prediksi-code')
@with_appcontext
def test_prediksi_code():
    dbsession = _create_session()
    nur = dbsession.query(DsetRow).filter(DsetRow.id == 138).first()
    # rambu_day = dbsession.query(DsetRow).filter(DsetRow.id == 10).first()
    print(f"Prediksi Nur={nur.prediksi_code}")
    # print(f"Prediksi Rambu Day={rambu_day.prediksi_code}")

def db_session_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        db_session = g.pop('db_session', None)
        if db_session is None:
            g.db_session = _create_session()
        return f(*args, **kwargs)
    return wrap

# Remove the session from request context and close it.
# What the fuck is 'e'
def close_session(e=None):
    session = g.pop('dbsession', None)
    if session is not None:
        session.close()

# Register session lifecycle hook to instance.
# Using function since we use factory.
def init_app(app=None):
    if app is None: raise Exception('App is none!')
    app.teardown_appcontext(close_session)
    app.cli.add_command(init_db)
    app.cli.add_command(do_seed)
    app.cli.add_command(test_prediksi_code)