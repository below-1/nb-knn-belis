import json
from flask import render_template
from flask import request
from flask import redirect
from flask import g
from flask import session
from serafim.model import DsetRow
from serafim.model import converter
from serafim.model import User
from serafim.model import db_session_required
from serafim.nb import NaiveBayesV2
from serafim.services import nrb
from serafim.user.blueprint import user_blueprint
from serafim.auth import user_required
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

@user_blueprint.route('/')
def user_landing():
    return render_template('user/index.html')

@user_blueprint.route('/prediksi-form')
def user_prediksi_form():
    return render_template('user/prediksi-form.html')

@user_blueprint.route('/prediksi', methods=['GET', 'POST'])
@db_session_required
def user_prediksi():
    form = request.json
    dset_row = DsetRow()
    dset_row = converter.dset_from_dict(dset_row, form)

    # Exclude target and id
    vector, _, __ = converter.dset_to_vector(dset_row)

    db_session = g.get('db_session')
    raw_data = db_session.query(DsetRow).filter(DsetRow.is_kasus == True).all()
    dataset = list(map(converter.dset_to_vector, raw_data))
    # raise Exception('Here')
    naive_bayes = NaiveBayesV2(dataset, 6)
    result = naive_bayes.run(vector)

    most_sim_id = result['max_knn_row_id']
    most_sim_case = db_session.query(DsetRow).filter(DsetRow.id == most_sim_id).first()

    password = generate_password_hash('random')
    username = 'random'
    role = 'user'
    nama = 'random'
    user = User(username=username, role=role, password=password, nama=nama)
    db_session.add(user)
    db_session.commit()

    dset_row.user_id = user.id
    dset_row.mamuli_kaki = most_sim_case.mamuli_kaki
    dset_row.mamuli_polos = most_sim_case.mamuli_polos
    dset_row.kuda = most_sim_case.kuda
    dset_row.kerbau = most_sim_case.kerbau
    dset_row.sapi = most_sim_case.sapi
    dset_row.uang = most_sim_case.uang
    dset_row.is_record = True
    dset_row.is_kasus = True
    dset_row.similarity = result['max_knn_sim']

    return json.dumps({
        'status': 'valid',
        'mamuli_kaki': dset_row.mamuli_kaki,
        'mamuli_polos': dset_row.mamuli_polos,
        'kuda': dset_row.kuda,
        'kerbau': dset_row.kerbau,
        'sapi': dset_row.sapi,
        'uang': dset_row.uang,
        'jumlah_belis': nrb.prediksi_code(dset_row).name,
        'similarity': dset_row.similarity
    })


@user_blueprint.route('/addUserIfNeeded/<user_id>', methods=['GET', 'POST'])
@db_session_required
def add_user_if_needed (user_id):
    dbsession = g.get('db_session')
    user = dbsession.query(User).filter_by(fb_id=user_id).first()

    if user: return json.dumps({ 'status': 'exists', 'user': user.as_dict() })
    nama = f"user-{user_id}"
    username = f"user-{user_id}"
    role = "user"
    password = username
    user = User(nama=nama, username=username, role=role, password=password, fb_id=user_id)
    dbsession.add(user)
    dbsession.commit()
    return json.dumps({
        'user': user.as_dict(),
        'status': 'created'
    })
