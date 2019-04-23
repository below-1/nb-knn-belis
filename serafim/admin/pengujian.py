from flask import request
from flask import render_template
from flask import session
from flask import g
from serafim.auth import admin_required
from serafim.admin.blueprint import admin_blueprint
from serafim.model import db_session_required
from serafim.model import DsetRow
from serafim.model import TingkatPendidikan
from serafim.model import StatusAdat
from serafim.model import Pekerjaan
from serafim.model import TingkatEkonomi
from serafim.model import converter
from serafim.nb import NaiveBayesV2
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
    result = naive_bayes.run(vector)

    most_sim_id = result['max_knn_row_id']
    most_sim_case = db_session.query(DsetRow).filter(DsetRow.id == most_sim_id).first()

    dset_row.user_id = session['user_id']
    dset_row.mamuli_kaki = most_sim_case.mamuli_kaki
    dset_row.mamuli_polos = most_sim_case.mamuli_polos
    dset_row.kuda = most_sim_case.kuda
    dset_row.kerbau = most_sim_case.kerbau
    dset_row.sapi = most_sim_case.sapi
    dset_row.uang = most_sim_case.uang
    dset_row.is_record = True
    dset_row.is_kasus = True
    dset_row.similarity = result['max_knn_sim']

    return render_template("admin/pengujian/single-ok-result.html",
                           new_case=dset_row,
                           most_sim_case=most_sim_case,
                           result=result)


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
    kfold_result = kfold(dataset, k)
    print('kfold_result.accuracy=', kfold_result.accuracy)
    print('kfold_result.total_hit=', kfold_result.total_hit)
    return render_template('admin/pengujian/dataset-result.html',
                           kfold_result=kfold_result,
                           k=k)