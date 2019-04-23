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
from serafim.model import converter
from serafim.admin.util import DSET_FORM_OPTIONS

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
    dset_row = converter.dset_from_dict(dset_row, form)

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
