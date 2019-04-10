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

@admin_blueprint.route('/dataset')
@admin_required
@db_session_required
def admin_list_dataset():
    show_detail_profile = request.args.get('show_detail_profile')
    show_detail_belis = request.args.get('show_detail_belis')

    print('show = ', type(show_detail_profile))

    show_detail_profile = True if show_detail_profile is not None else False
    show_detail_belis = True if show_detail_belis is not None else False

    db_session = g.get('db_session')
    dataset = db_session.query(DsetRow).filter(DsetRow.is_kasus == True).all()
    print(dataset)
    print([ row.usia for row in dataset ])
    return render_template("admin/dataset/list.html",
      items=dataset,
      show_detail_profile=show_detail_profile,
      show_detail_belis=show_detail_belis
    )

@admin_blueprint.route('/dataset/create', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_create_dataset():
    if request.method == 'GET':
        return render_template("admin/dataset/create.html", options=DSET_FORM_OPTIONS)

    form = request.form
    dset_row = DsetRow()
    dset_row = converter.kasus_from_dict(dset_row, form)

    user_id = int(session['user_id'])
    dset_row.user_id = int(user_id)

    db_session = g.get('db_session')
    db_session.add(dset_row)
    db_session.commit()
    return redirect(url_for("admin.admin_list_dataset"))

@admin_blueprint.route('/dataset/update/<id>', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_update_dataset(id):
    db_session = g.get('db_session')
    if request.method == 'GET':
        dset_row = db_session.query(DsetRow).filter(DsetRow.id == id).first()
        return render_template("admin/dataset/update.html",
                               dset_row=dset_row,
                               options=DSET_FORM_OPTIONS)
    form = request.form
    dset_row = db_session.query(DsetRow).filter(DsetRow.id == id).first()
    dset_row = converter.kasus_from_dict(dset_row, form)
    db_session.commit()
    return redirect(url_for("admin.admin_list_dataset"))

@admin_blueprint.route('/dataset/delete/<id>', methods=['GET'])
@admin_required
@db_session_required
def admin_delete_dataset(id):
    db_session = g.get('db_session')
    db_session.query(DsetRow).filter_by(id=id).delete()
    db_session.commit()
    return redirect(url_for('admin.admin_list_dataset'))