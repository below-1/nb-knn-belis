from random import shuffle
from flask import request
from flask import render_template
from flask import session
from flask import g
from serafim.auth import admin_required
from serafim.admin.blueprint import admin_blueprint
from serafim.model import db_session_required
from serafim.model import DsetRow
from serafim.model import converter
from serafim.nb import NaiveBayesV2, construct_solution
from serafim.kfold import kfold
from serafim.admin.util import  DSET_FORM_OPTIONS

@admin_blueprint.route('/pengujian/single', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_pengujian_single():
    if request.method == 'GET':
        return render_template("admin/pengujian/single-form.html",
          options=DSET_FORM_OPTIONS
        )

    form = request.form
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

    dset_row.user_id = session['user_id']
    dset_row.mamuli_kaki = knn_attr[0]
    dset_row.mamuli_polos = knn_attr[1]
    dset_row.kuda = knn_attr[2]
    dset_row.kerbau = knn_attr[3]
    dset_row.sapi = knn_attr[4]
    dset_row.uang = knn_attr[5]
    dset_row.is_record = True
    dset_row.is_kasus = True
    dset_row.similarity = knn_result.similarity

    return render_template("admin/pengujian/single-ok-result.html",
                           new_case=dset_row,
                           classification=classification,
                           knn_result=knn_result,
                           knn_attr=knn_attr)


@admin_blueprint.route('/pengujian/dataset', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_pengujian_dataset():
    if request.method == 'GET':
        return render_template('admin/pengujian/dataset-form.html')

    k = int(request.form['k'])
    db_session = g.get('db_session')
    raw_data = db_session.query(DsetRow).filter(DsetRow.is_kasus == True).all()
    dataset = list(map(converter.dset_to_vector, raw_data))
    shuffle(dataset)
    kfold_result = kfold(dataset, k)
    return render_template('admin/pengujian/dataset-result.html',
                           kfold_result=kfold_result,
                           k=k)