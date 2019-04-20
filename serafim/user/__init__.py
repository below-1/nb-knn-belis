from flask import render_template
from flask import request
from flask import g
from flask import session
from serafim.model import DsetRow
from serafim.model import converter
from serafim.model import db_session_required
from serafim.nb import NaiveBayesV2
from serafim.user.blueprint import user_blueprint

@user_blueprint.route('/')
def user_landing():
    return render_template('index.html')

@user_blueprint.route('/prediksi', methods=['GET', 'POST'])
@db_session_required
def user_prediksi():
    form = request.form
    dset_row = DsetRow()
    dset_row = converter.kasus_from_dict(dset_row, form)

    # Exclude target and id
    vector, _, __ = converter.dset_to_vector(dset_row)

    db_session = g.get('db_session')
    raw_data = db_session.query(DsetRow).filter(DsetRow.is_kasus == True).all()
    dataset = list(map(converter.dset_to_vector, raw_data))
    naive_bayes = NaiveBayesV2(dataset, 6)
    result = naive_bayes.run(vector)

    # If similarity is greater than 80% save it to database.
    if result['max_knn_sim'] >= 0.8:
        # First we need to copy the solusi.
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

        return render_template("prediksi-result.html",
                               dset_row=dset_row,
                               result=result)

    return render_template("prediksi/single-fail-result.html", result=result)