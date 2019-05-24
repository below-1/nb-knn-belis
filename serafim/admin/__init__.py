from flask import render_template
from flask import g
from sqlalchemy import func
from serafim.admin.blueprint import admin_blueprint
from serafim.model import db_session_required
from serafim.model import DsetRow
from serafim.model import ThreeLevelEnum

# Import route functions
from serafim.admin import dataset
from serafim.admin import revisi
from serafim.admin import data_user
from serafim.admin import pengujian
from serafim.admin import rule
from serafim.auth import admin_required
from serafim.services import nrb

@admin_blueprint.route('/')
@admin_required
@db_session_required
def admin_dashboard():
    db_session = g.get('db_session')
    all_record = db_session.query(DsetRow).all()
    is_low = lambda r: nrb.prediksi_code(r) == ThreeLevelEnum.RENDAH
    is_mid = lambda r: nrb.prediksi_code(r) == ThreeLevelEnum.SEDANG
    is_high = lambda r: nrb.prediksi_code(r) == ThreeLevelEnum.TINGGI

    total_record = len(all_record)
    total_case = len([ r for r in all_record if r.is_kasus ])
    total_low = len([ r for r in all_record if r.is_kasus and is_low(r) ])
    total_mid = len([ r for r in all_record if r.is_kasus and is_mid(r) ])
    total_high = len([ r for r in all_record if r.is_kasus and is_high(r) ])

    result = {
        'total_record': total_record,
        'total_case': total_case,
        'total_low': total_low,
        'total_mid': total_mid,
        'total_high': total_high
    }
    return render_template('admin/dashboard.html', **result)

