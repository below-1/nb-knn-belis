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
from serafim.model import converter
from serafim.admin.util import DSET_FORM_OPTIONS
from serafim.services import nrb

@admin_blueprint.route('/dataset/test')
@admin_required
@db_session_required
def foobar():
    mock_dset = DsetRow()
    mock_dset.mamuli_kaki = 0
    mock_dset.mamuli_polos = 12
    mock_dset.kuda = 23
    mock_dset.kerbau = 8
    mock_dset.sapi = 8
    mock_dset.uang = 7000000
    row = (
        ThreeLevelEnum.RENDAH,
        ThreeLevelEnum.RENDAH,
        ThreeLevelEnum.SEDANG,
        ThreeLevelEnum.SEDANG,
        ThreeLevelEnum.SEDANG,
        ThreeLevelEnum.SEDANG
    )
    gen_row = (
        mock_dset.mamulu_kaki_code,
        mock_dset.mamulu_polos_code,
        mock_dset.kuda_code,
        mock_dset.kerbau_code,
        mock_dset.sapi_code,
        mock_dset.uang_code
    )
    print(row)
    print(gen_row == row)
    print(nrb.check(row))
    return "OK"

@admin_blueprint.route('/dataset')
@admin_required
@db_session_required
def admin_list_dataset():
    '''
    Show all data.
    '''
    show_detail_profile = request.args.get('show_detail_profile')
    show_detail_belis = request.args.get('show_detail_belis')

    show_detail_profile = True if show_detail_profile is not None else False
    show_detail_belis = True if show_detail_belis is not None else False

    db_session = g.get('db_session')
    dataset = db_session.query(DsetRow).filter(DsetRow.is_kasus == True).all()
    return render_template("admin/dataset/list.html",
      items=dataset,
      show_detail_profile=show_detail_profile,
      show_detail_belis=show_detail_belis,
      nrb=nrb
    )

@admin_blueprint.route('/dataset/create', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_create_dataset():
    if request.method == 'GET':
        return render_template("admin/dataset/create.html", options=DSET_FORM_OPTIONS)

    form = request.form
    drow = DsetRow()
    drow = converter.dset_from_dict(drow, form)
    if (not nrb.check_drow(drow)):
        # Add to rule base
        row = ( drow.mamulu_kaki_code, drow.mamulu_polos_code, drow.kuda_code, drow.kerbau_code, drow.sapi_code, drow.uang_code, nrb.prediksi_code(drow) )
        nrb.add_rule(row)

    user_id = int(session['user_id'])
    drow.user_id = int(user_id)

    db_session = g.get('db_session')
    db_session.add(drow)
    db_session.commit()
    return redirect(url_for("admin.admin_list_dataset"))

@admin_blueprint.route('/dataset/update/<id>', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_update_dataset(id):
    db_session = g.get('db_session')
    if request.method == 'GET':
        dset_row = db_session.query(DsetRow).filter(DsetRow.id == id).first()
        print(nrb.prediksi_code(dset_row))
        return render_template("admin/dataset/update.html",
                               dset_row=dset_row,
                               options=DSET_FORM_OPTIONS)
    form = request.form
    dset_row = db_session.query(DsetRow).filter(DsetRow.id == id).first()
    dset_row = converter.dset_from_dict(dset_row, form)
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
