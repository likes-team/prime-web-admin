from datetime import datetime
import decimal
from prime_admin.globals import get_date_now
from flask import redirect, url_for
from flask.json import jsonify
from flask.templating import render_template
from flask_login import login_required, current_user
from werkzeug.wrappers import ResponseStream
from app.core.models import CoreModule, CoreModel
from prime_admin import bp_lms
from prime_admin.models import Branch, CashFlow, Dashboard, Registration
from app.admin.templating import admin_dashboard, DashboardBox
from mongoengine.queryset.visitor import Q
from config import TIMEZONE



JANSTART = datetime(2021, 1, 1)
JANEND = datetime(2021, 1, 31)
FEBSTART = datetime(2021, 2, 1)
FEBEND = datetime(2021, 2, 28)
MARSTART = datetime(2021, 3, 1)
MAREND = datetime(2021, 3, 31)
APRSTART = datetime(2021, 4, 1)
APREND = datetime(2021, 4, 30)
MAYSTART = datetime(2021, 5, 1)
MAYEND = datetime(2021, 5, 31)
JUNSTART = datetime(2021, 6, 1)
JUNEND = datetime(2021, 6, 30)
JULSTART = datetime(2021, 7, 1)
JULEND = datetime(2021, 7, 31)
AUGSTART = datetime(2021, 8, 1)
AUGEND = datetime(2021, 8, 31)
SEPSTART = datetime(2021, 9, 1)
SEPEND = datetime(2021, 9, 30)
OCTSTART = datetime(2021, 10, 1)
OCTEND = datetime(2021, 10, 31)
NOVSTART = datetime(2021, 11, 1)
NOVEND = datetime(2021, 11, 30)
DECSTART = datetime(2021, 12, 1)
DECEND = datetime(2021, 12, 31)


@bp_lms.route('/')
@bp_lms.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name == "Secretary":
        return redirect(url_for('lms.members'))

    if current_user.role.name != "Admin":
        return render_template('auth/authorization_error.html')

    from app.auth.models import User
    
    options = {
        'branches': Branch.objects(),
        'box1': DashboardBox("Number of enrollees","Current", 0),
        'box2': DashboardBox("Total Sales","Montly", 0),
        'box3': DashboardBox("Gross Income","Total users", 0),
        'scripts': [{'lms.static': 'js/utils.js'}, {'lms.static': 'js/dashboard.js'}]
    }

    return admin_dashboard(
        Dashboard,
        **options,
        dashboard_template="lms/dashboard.html",
        module="learning_management",
        
    )


@bp_lms.route('/api/dashboard/get-chart-data/<string:branch_id>', methods=['GET'])
@login_required
def get_chart_data(branch_id):
    gross_sales = []
    expenses = []
    maintaining_sales = []
    net = []
    no_of_students = []

    sale_jan = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=JANSTART) & Q(date_deposit__lte=JANEND)).order_by("-date_deposit").first()
    sale_feb = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=FEBSTART) & Q(date_deposit__lte=FEBEND)).order_by("-date_deposit").first()
    sale_mar = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=MARSTART) & Q(date_deposit__lte=MAREND)).order_by("-date_deposit").first()
    sale_apr = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=APRSTART) & Q(date_deposit__lte=APREND)).order_by("-date_deposit").first()
    sale_may = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=MAYSTART) & Q(date_deposit__lte=MAYEND)).order_by("-date_deposit").first()
    sale_jun = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=JUNSTART) & Q(date_deposit__lte=JUNEND)).order_by("-date_deposit").first()
    sale_jul = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=JULSTART) & Q(date_deposit__lte=JULEND)).order_by("-date_deposit").first()
    sale_aug = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=AUGSTART) & Q(date_deposit__lte=AUGEND)).order_by("-date_deposit").first()
    sale_sep = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=SEPSTART) & Q(date_deposit__lte=SEPEND)).order_by("-date_deposit").first()
    sale_oct = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=OCTSTART) & Q(date_deposit__lte=OCTEND)).order_by("-date_deposit").first()
    sale_nov = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=NOVSTART) & Q(date_deposit__lte=NOVEND)).order_by("-date_deposit").first()
    sale_dec = CashFlow.objects(branch=branch_id).filter(Q(date_deposit__gte=DECSTART) & Q(date_deposit__lte=DECEND)).order_by("-date_deposit").first()

    gross_sales_per_month = {
        'jan': str(sale_jan.balance) if sale_jan is not None else 0,
        'feb': str(sale_feb.balance) if sale_feb is not None else 0,
        'mar': str(sale_mar.balance) if sale_mar is not None else 0,
        'apr': str(sale_apr.balance) if sale_apr is not None else 0,
        'may': str(sale_may.balance) if sale_may is not None else 0,
        'jun': str(sale_jun.balance) if sale_jun is not None else 0,
        'jul': str(sale_jul.balance) if sale_jul is not None else 0,
        'aug': str(sale_aug.balance) if sale_aug is not None else 0,
        'sep': str(sale_sep.balance) if sale_sep is not None else 0,
        'oct': str(sale_oct.balance) if sale_oct is not None else 0,
        'nov': str(sale_nov.balance) if sale_nov is not None else 0,
        'dec': str(sale_dec.balance) if sale_dec is not None else 0,
    }

    gross_sales.append(gross_sales_per_month['jan'])
    gross_sales.append(gross_sales_per_month['feb'])
    gross_sales.append(gross_sales_per_month['mar'])
    gross_sales.append(gross_sales_per_month['apr'])
    gross_sales.append(gross_sales_per_month['may'])
    gross_sales.append(gross_sales_per_month['jun'])
    gross_sales.append(gross_sales_per_month['jul'])
    gross_sales.append(gross_sales_per_month['aug'])
    gross_sales.append(gross_sales_per_month['sep'])
    gross_sales.append(gross_sales_per_month['oct'])
    gross_sales.append(gross_sales_per_month['nov'])
    gross_sales.append(gross_sales_per_month['dec'])

    net_percent = decimal.Decimal(".55")

    net_per_month = {
        'jan': str(sale_jan.balance * net_percent) if sale_jan is not None else 0,
        'feb': str(sale_feb.balance * net_percent) if sale_feb is not None else 0,
        'mar': str(sale_mar.balance * net_percent) if sale_mar is not None else 0,
        'apr': str(sale_apr.balance * net_percent) if sale_apr is not None else 0,
        'may': str(sale_may.balance * net_percent) if sale_may is not None else 0,
        'jun': str(sale_jun.balance * net_percent) if sale_jun is not None else 0,
        'jul': str(sale_jul.balance * net_percent) if sale_jul is not None else 0,
        'aug': str(sale_aug.balance * net_percent) if sale_aug is not None else 0,
        'sep': str(sale_sep.balance * net_percent) if sale_sep is not None else 0,
        'oct': str(sale_oct.balance * net_percent) if sale_oct is not None else 0,
        'nov': str(sale_nov.balance * net_percent) if sale_nov is not None else 0,
        'dec': str(sale_dec.balance * net_percent) if sale_dec is not None else 0,
    }

    net.append(net_per_month['jan'])
    net.append(net_per_month['feb'])
    net.append(net_per_month['mar'])
    net.append(net_per_month['apr'])
    net.append(net_per_month['may'])
    net.append(net_per_month['jun'])
    net.append(net_per_month['jul'])
    net.append(net_per_month['aug'])
    net.append(net_per_month['sep'])
    net.append(net_per_month['oct'])
    net.append(net_per_month['nov'])
    net.append(net_per_month['dec'])

    expenses_per_month = {
        'jan': Registration.objects(status='registered').filter(Q(created_at__gte=JANSTART) & Q(created_at__lte=JANEND)).sum('amount'),
        'feb': Registration.objects(status='registered').filter(Q(created_at__gte=FEBSTART) & Q(created_at__lte=FEBEND)).sum('amount'),
        'mar': Registration.objects(status='registered').filter(Q(created_at__gte=MARSTART) & Q(created_at__lte=MAREND)).sum('amount'),
        'apr': Registration.objects(status='registered').filter(Q(created_at__gte=APRSTART) & Q(created_at__lte=APREND)).sum('amount'),
        'may': Registration.objects(status='registered').filter(Q(created_at__gte=MAYSTART) & Q(created_at__lte=MAYEND)).sum('amount'),
        'jun': Registration.objects(status='registered').filter(Q(created_at__gte=JUNSTART) & Q(created_at__lte=JUNEND)).sum('amount'),
        'jul': Registration.objects(status='registered').filter(Q(created_at__gte=JULSTART) & Q(created_at__lte=JULEND)).sum('amount'),
        'aug': Registration.objects(status='registered').filter(Q(created_at__gte=AUGSTART) & Q(created_at__lte=AUGEND)).sum('amount'),
        'sep': Registration.objects(status='registered').filter(Q(created_at__gte=SEPSTART) & Q(created_at__lte=SEPEND)).sum('amount'),
        'oct': Registration.objects(status='registered').filter(Q(created_at__gte=OCTSTART) & Q(created_at__lte=OCTEND)).sum('amount'),
        'nov': Registration.objects(status='registered').filter(Q(created_at__gte=NOVSTART) & Q(created_at__lte=NOVEND)).sum('amount'),
        'dec': Registration.objects(status='registered').filter(Q(created_at__gte=DECSTART) & Q(created_at__lte=DECEND)).sum('amount'),
    }

    # expenses.append(expenses_per_month['jan'])
    # expenses.append(expenses_per_month['feb'])
    # expenses.append(expenses_per_month['mar'])
    # expenses.append(expenses_per_month['apr'])
    # expenses.append(expenses_per_month['may'])
    # expenses.append(0)
    # expenses.append(expenses_per_month['jul'])
    # expenses.append(expenses_per_month['aug'])
    # expenses.append(expenses_per_month['sep'])
    # expenses.append(expenses_per_month['oct'])
    # expenses.append(expenses_per_month['nov'])
    # expenses.append(expenses_per_month['dec'])

    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)
    expenses.append(0)

    no_of_students_per_month = {
        'jan': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=JANSTART) & Q(created_at__lte=JANEND)).count(),
        'feb': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=FEBSTART) & Q(created_at__lte=FEBEND)).count(),
        'mar': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=MARSTART) & Q(created_at__lte=MAREND)).count(),
        'apr': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=APRSTART) & Q(created_at__lte=APREND)).count(),
        'may': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=MAYSTART) & Q(created_at__lte=MAYEND)).count(),
        'jun': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=JUNSTART) & Q(created_at__lte=JUNEND)).count(),
        'jul': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=JULSTART) & Q(created_at__lte=JULEND)).count(),
        'aug': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=AUGSTART) & Q(created_at__lte=AUGEND)).count(),
        'sep': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=SEPSTART) & Q(created_at__lte=SEPEND)).count(),
        'oct': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=OCTSTART) & Q(created_at__lte=OCTEND)).count(),
        'nov': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=NOVSTART) & Q(created_at__lte=NOVEND)).count(),
        'dec': Registration.objects(status='registered').filter(branch=branch_id).filter(Q(created_at__gte=DECSTART) & Q(created_at__lte=DECEND)).count(),
    }

    no_of_students.append(no_of_students_per_month['jan'])
    no_of_students.append(no_of_students_per_month['feb'])
    no_of_students.append(no_of_students_per_month['mar'])
    no_of_students.append(no_of_students_per_month['apr'])
    no_of_students.append(no_of_students_per_month['may'])
    no_of_students.append(no_of_students_per_month['jun'])
    no_of_students.append(no_of_students_per_month['jul'])
    no_of_students.append(no_of_students_per_month['aug'])
    no_of_students.append(no_of_students_per_month['sep'])
    no_of_students.append(no_of_students_per_month['oct'])
    no_of_students.append(no_of_students_per_month['nov'])
    no_of_students.append(no_of_students_per_month['dec'])

    maintaining_sales = [
        85000,85000,85000,85000,85000,85000,85000,85000,85000,85000,85000,85000,
    ]

    month_count = get_date_now().month

    response = {
        'gross_sales': gross_sales[:month_count],
        'net': net[:month_count],
        'maintaining_sales': maintaining_sales[: month_count],
        'expenses': expenses[:month_count],
        'no_of_students': no_of_students
    }

    return jsonify(response)
