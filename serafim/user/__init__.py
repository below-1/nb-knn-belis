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
from serafim.nb import NaiveBayesV2, construct_solution
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
    naive_bayes = NaiveBayesV2(dataset, 6)
    naive_bayes.build()
    classification = naive_bayes.classify(vector)
    knn_result = naive_bayes.knn(vector, classification.clazz)
    knn_attr = construct_solution(db_session, knn_result.selected_ids)

    dset_row.mamuli_kaki = knn_attr[0]
    dset_row.mamuli_polos = knn_attr[1]
    dset_row.kuda = knn_attr[2]
    dset_row.kerbau = knn_attr[3]
    dset_row.sapi = knn_attr[4]
    dset_row.uang = knn_attr[5]
    dset_row.is_record = True
    dset_row.is_kasus = True
    dset_row.similarity = knn_result.similarity

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
