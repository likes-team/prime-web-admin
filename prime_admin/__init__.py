from flask import Blueprint
from app.auth.models import Role


bp_lms = Blueprint('lms', __name__, template_folder='templates', static_folder='static',\
    static_url_path='/lms/static')


from . import views
from . import datatables