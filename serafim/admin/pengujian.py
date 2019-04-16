import json
from flask import request
from flask import render_template
from flask import session
from flask import g
from flask import url_for
from flask import redirect
from serafim.auth import admin_required
from serafim.admin.blueprint import admin_blueprint
from serafim.model import db_session_required
from serafim.model import DsetRow
from serafim.model import ThreeLevelEnum
from serafim.model import TingkatPendidikan
from serafim.model import StatusAdat
from serafim.model import Pekerjaan
from serafim.model import TingkatEkonomi
from serafim.model import converter
from serafim.nb import NaiveBayesV2

DSET_FORM_OPTIONS = {
    'status_adat': [
        ('Hamba', StatusAdat.HAMBA.name),
        ('Biasa', StatusAdat.BIASA.name),
        ('Maramba', StatusAdat.MARAMBA.name),
        ('Bangsawan', StatusAdat.BANGSAWAN.name)
    ],
    'tingkat_pendidikan': [
        ('Tidak Sekolah', TingkatPendidikan.TIDAK_SEKOLAH.name),
        ('SD', TingkatPendidikan.SD.name),
        ('SMP', TingkatPendidikan.SMP.name),
        ('SMA', TingkatPendidikan.SMA.name),
        ('D3', TingkatPendidikan.D3.name),
        ('S1', TingkatPendidikan.S1.name),
        ('S2', TingkatPendidikan.S2.name),
        ('S3', TingkatPendidikan.S3.name)
    ],
    'pekerjaan': [
        ('Petani', Pekerjaan.PETANI.name),
        ('Honorer / Pegawai Tidak Tetap', Pekerjaan.HONORER_PTT.name),
        ('PNS', Pekerjaan.PNS.name),
        ('Tenun Ikat', Pekerjaan.TENUN_IKAT.name)
    ],
    'tingkat_ekonomi': [
        ('Rendah', TingkatEkonomi.RENDAH.name),
        ('Sedang', TingkatEkonomi.SEDANG.name),
        ('Tinggi', TingkatEkonomi.TINGGI.name)
    ]
}

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

        db_session.add(dset_row)
        db_session.commit()

        return render_template("admin/pengujian/single-ok-result.html",
                               new_case=dset_row,
                               most_sim_case=most_sim_case,
                               result=result)

    dset_row.mamuli_kaki = 0
    dset_row.mamuli_polos = 0
    dset_row.kuda = 0
    dset_row.kerbau = 0
    dset_row.sapi = 0
    dset_row.uang = 0

    dset_row.is_record = True
    dset_row.is_kasus = False
    dset_row.similarity = result['max_knn_sim']
    dset_row.user_id = session['user_id']

    db_session.add(dset_row)
    db_session.commit()

    # If not, tell user that he/she need to change the solusi first.
    # And save the data as revisi
    return render_template("admin/pengujian/single-fail-result.html", result=result)