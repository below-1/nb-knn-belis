from flask import request
from flask import render_template
from flask import g
from flask import url_for
from flask import redirect
from serafim.auth import admin_required
from serafim.admin.blueprint import admin_blueprint
from serafim.model import db_session_required
from serafim.model import DsetRow
from serafim.model import TingkatPendidikan
from serafim.model import StatusAdat
from serafim.model import Pekerjaan
from serafim.model import TingkatEkonomi
from serafim.admin.util import DSET_FORM_OPTIONS


@admin_blueprint.route('/revisi')
@admin_required
@db_session_required
def admin_list_revisi():
    show_detail_profile = request.args.get('show_detail_profile')
    show_detail_belis = request.args.get('show_detail_belis')

    print('show = ', type(show_detail_profile))

    show_detail_profile = True if show_detail_profile is not None else False
    show_detail_belis = True if show_detail_belis is not None else False

    db_session = g.get('db_session')
    dataset = db_session.query(DsetRow).filter(DsetRow.is_kasus == False, DsetRow.similarity < 0.8).all()
    print(dataset)
    print([ row.usia for row in dataset ])
    return render_template("admin/revisi/list.html",
      items=dataset,
      show_detail_profile=show_detail_profile,
      show_detail_belis=show_detail_belis
    )


@admin_blueprint.route('/revisi/update/<id>', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_update_revisi(id):
    db_session = g.get('db_session')
    if request.method == 'GET':
        dset_row = db_session.query(DsetRow).filter(DsetRow.id == id).first()
        return render_template("admin/revisi/update.html",
                               dset_row=dset_row,
                               options=DSET_FORM_OPTIONS)
    data = request.form
    dset_row = db_session.query(DsetRow).filter(DsetRow.id == id).first()
    # Each field is optional. so we need guards.
    if 'mamuli_kaki' in data:
        dset_row.mamuli_kaki = int(data['mamuli_kaki'])
    if 'mamuli_polos' in data:
        dset_row.mamuli_polos = int(data['mamuli_polos'])
    if 'kuda' in data:
        dset_row.kuda = int(data['kuda'])
    if 'kerbau' in data:
        dset_row.kerbau = int(data['kerbau'])
    if 'sapi' in data:
        dset_row.sapi = int(data['sapi'])
    if 'uang' in data:
        dset_row.uang = int(data['uang'])
    dset_row.is_kasus = True
    db_session.commit()
    return redirect(url_for("admin.admin_list_revisi"))

@admin_blueprint.route('/revisi/delete/<id>', methods=['GET'])
@admin_required
@db_session_required
def admin_delete_revisi(id):
    db_session = g.get('db_session')
    db_session.query(DsetRow).filter_by(id=id).delete()
    db_session.commit()
    return redirect(url_for('admin.admin_list_revisi'))