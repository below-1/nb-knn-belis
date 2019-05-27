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
from serafim.admin.util import RULE_OPTIONS
from serafim.services import nrb

def _format(x):
    if x == ThreeLevelEnum.RENDAH: return "Rendah"
    elif x == ThreeLevelEnum.SEDANG: return "Sedang"
    elif x == ThreeLevelEnum.TINGGI: return "Tinggi"
    else:
        raise Exception(f"can't find rule for {x}")

@admin_blueprint.route('/rule/recover')
@admin_required
@db_session_required
def recover():
    nrb.write()
    return "OK"

@admin_blueprint.route('/rule')
@admin_required
@db_session_required
def admin_list_rule():
    '''
    Show all data.
    '''
    rules = nrb.data
    return render_template("admin/rule/list.html",
      rules=rules,
      _format=_format
    )


@admin_blueprint.route('/rule/create', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_rule_create():
    if request.method == 'GET':
        return render_template("admin/rule/create.html", rule_options=RULE_OPTIONS)
    form = request.form
    print("form=", form)
    mk = form['mamuli_kaki']
    mp = form['mamuli_polos']
    kuda = form['kuda']
    kerbau = form['kerbau']
    sapi = form['sapi']
    uang = form['uang']
    jumlah = form['jumlah']

    mk = ThreeLevelEnum[mk]
    mp = ThreeLevelEnum[mp]
    kuda = ThreeLevelEnum[kuda]
    kerbau = ThreeLevelEnum[kerbau]
    sapi = ThreeLevelEnum[sapi]
    uang = ThreeLevelEnum[uang]
    jumlah = ThreeLevelEnum[jumlah]

    # Must be tuple
    row = (mk, mp, kuda, kerbau, sapi, uang, jumlah)
    # print(row)
    is_exists = nrb.check_complete(row)
    if is_exists:
        return render_template("admin/rule/already-exist.html")

    nrb.add_rule(row)
    nrb.write()
    return redirect(url_for("admin.admin_list_rule"))

@admin_blueprint.route('/rule/update/<idx>', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_rule_update(idx):
    if request.method == 'GET':
        rules = nrb.data
        rule = rules[int(idx)]
        return render_template("admin/rule/update.html", rule_options=RULE_OPTIONS, rule=rule)
    form = request.form
    print("form=", form)
    mk = form['mamuli_kaki']
    mp = form['mamuli_polos']
    kuda = form['kuda']
    kerbau = form['kerbau']
    sapi = form['sapi']
    uang = form['uang']
    jumlah = form['jumlah']

    mk = ThreeLevelEnum[mk]
    mp = ThreeLevelEnum[mp]
    kuda = ThreeLevelEnum[kuda]
    kerbau = ThreeLevelEnum[kerbau]
    sapi = ThreeLevelEnum[sapi]
    uang = ThreeLevelEnum[uang]
    jumlah = ThreeLevelEnum[jumlah]

    # Must be tuple
    row = (mk, mp, kuda, kerbau, sapi, uang, jumlah)
    # print(row)
    is_exists = nrb.check_complete(row)
    if is_exists:
        return render_template("admin/rule/already-exist.html")

    nrb.update_rule(int(idx), row)
    nrb.write()
    return redirect(url_for("admin.admin_list_rule"))

@admin_blueprint.route('/rule/remove/<pos>', methods=['GET', 'POST'])
@admin_required
@db_session_required
def admin_rule_remove(pos):
    nrb.remove_rule(int(pos))
    return redirect(url_for("admin.admin_list_rule"))