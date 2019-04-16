from flask import render_template
from serafim.admin.blueprint import admin_blueprint

@admin_blueprint.route('/')
def admin_dashboard():
    return render_template('admin/dashboard.html')