from flask import render_template
from serafim.admin.blueprint import admin_blueprint

# Import route functions
from serafim.admin import dataset
from serafim.admin import data_user
from serafim.admin import pengujian

@admin_blueprint.route('/')
def admin_dashboard():
    return render_template('admin/dashboard.html')