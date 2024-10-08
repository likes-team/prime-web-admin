import decimal
from bson import Decimal128
from bson.objectid import ObjectId
from datetime import datetime
import pymongo
import pytz
from config import TIMEZONE
from flask import jsonify, request, render_template, abort
from flask_login import login_required, current_user
from flask_weasyprint import HTML, render_pdf
import inflect
from app import mongo
from app.auth.models import User
from prime_admin.globals import D128_CTX, convert_to_utc, get_date_now
from prime_admin import bp_lms
from prime_admin.models import Branch, FundWallet, Registration
from prime_admin.services.fund_wallet import BusinessExpensesService
from prime_admin.helpers.employee import get_employees
from prime_admin.helpers import access
from prime_admin.services.student import StudentService
from prime_admin.services.inventory import InventoryService
from prime_admin.helpers.query_filter import StudentQueryFilter
from prime_admin.models_v2 import StudentV2
from prime_admin.services.payment import PaymentService
from prime_admin.helpers.query_filter import PaymentQueryFilter
from prime_admin.models_v2 import PaymentV2
from prime_admin.utils.currency import convert_decimal128_to_decimal, format_to_str_php
from prime_admin.utils.date import format_utc_to_local


@bp_lms.route('/payroll')
@login_required
def payroll():
    if current_user.role.name not in ['Admin', 'Partner', 'Manager']:
        abort(404)

    branches = access.get_current_user_branches()
    return render_template(
        'lms/payroll/payroll_page.html', branches=branches, title="Payroll"
    )


@bp_lms.route('/payroll/create-payslip')
def create_payslip_page():
    branches = access.get_current_user_branches()
    return render_template(
        'lms/payroll/create_payslip_page.html', 
        branches=branches
    )
    

    
@bp_lms.route('/payroll/employees/<string:user_id>/edit', methods=['POST'])
def edit_payroll_employee(user_id):
    values = request.json['values']
    print(values)
    for i , val in enumerate(values):
        if val == '':
            values[i] = Decimal128(decimal.Decimal(0))
        else:
            values[i] = Decimal128(decimal.Decimal(val))
    
    salary_rate = values[0]
    ee_sss = values[1]
    ee_phil = values[2]
    ee_pag_ibig = values[3]
    er_sss = values[4]
    er_phil = values[5]
    er_pag_ibig = values[6]

    mongo.db.auth_users.update_one({
        '_id': ObjectId(user_id)
    }, {'$set': {
        'employee_information': {
            'salary_rate': salary_rate,
            'ee': {
                'sss': ee_sss,
                'phil': ee_phil,
                'pag_ibig': ee_pag_ibig
            },
            'er': {
                'sss': er_sss,
                'phil': er_phil,
                'pag_ibig': er_pag_ibig
            }
        }
    }})
    
    return jsonify({'result': True})


@bp_lms.route('/employees/<string:employee_id>/get-salary-rate', methods=['GET'])
def get_employee_salary_rate(employee_id):
    billing_month_from = request.args['billing_month_from']
    query = mongo.db.lms_fund_wallet_transactions.find_one({
        'description': employee_id, 'category': 'Bookeeper',
        'billing_month_from': billing_month_from
    })

    response = {
        'status': '',
        'data': {
            'salary_rate': 0,
            'government_benefits': 0
        }
    }
    
    if query is None:
        query = mongo.db.auth_users.find_one({"_id": ObjectId(employee_id)})
        employee_information = query.get('employee_information', {})
        salary_rate = str(employee_information.get('salary_rate', 0))

        response['data']['salary_rate'] = salary_rate
        response['message'] = "Retrieved Successfully!"
        response['status'] = 'success'
        return jsonify(response)
    
    # From bookeeper data
    employee_information = query.get('employee_information')
    ee = employee_information.get('ee')
    ee_sss = convert_decimal128_to_decimal(ee.get('sss', 0))
    ee_phil = convert_decimal128_to_decimal(ee.get('phil', 0))
    ee_pag_ibig = convert_decimal128_to_decimal(ee.get('pag_ibig', 0))
    goverment_benefits = str(ee_sss + ee_phil + ee_pag_ibig)

    # From users data
    query = mongo.db.auth_users.find_one({"_id": ObjectId(employee_id)})
    employee_information = query.get('employee_information', {})
    salary_rate = str(employee_information.get('salary_rate', 0))

    response['data']['salary_rate'] = salary_rate
    response['data']['government_benefits'] = goverment_benefits
    response['data']['sss'] = str(ee_sss)
    response['data']['phil_health'] = str(ee_phil)
    response['data']['pag_ibig'] = str(ee_pag_ibig)
    response['message'] = "Retrieved Successfully!"
    response['status'] = 'success'
    return jsonify(response)


@bp_lms.route('/payroll/create-payslip', methods=['POST'])
def create_payslip():
    form = request.form
    
    branch_id = form.get('branch')
    employee = form.get('employee')
    position = form.get('position')
    billing_month_from = form.get('billing_month_from', None)
    billing_month_to = form.get('billing_month_to', None)
    no_of_days = form.get('no_of_days', '0')
    day_off = form.get('day_off', '0')
    absent_days = form.get('absent_days', '0')
    total_working_days = form.get('total_working_days', '0')

    no_of_session = form.get('no_of_session', '0')
    if no_of_session == '': no_of_session = '0'

    salary_rate = form.get('salary_rate', '0')
    total_salary_amount = form.get("total_salary_amount", '0')
    food_allowance = form.get("food_allowance", '0')
    accommodation = form.get("accommodation", '0')
    holiday_pay = form.get("holiday_pay", '0')
    overtime_pay = form.get("overtime_pay", '0')
    month_13_pay = form.get("month_13_pay", '0')
    gross_salary = form.get('gross_salary', '0')
    cash_advance = form.get('cash_advance', '0')
    government_benefits = form.get('government_benefits', '0')
    accommodation_deduction = form.get("accommodation_deduction", '0')
    total_amount_due = form.get('total_amount_due', '0')
    settled_by = form.get('settled_by')

    sss = form.get('sss', '0')
    if sss == '': sss = '0'

    phil_health = form.get('phil_health', '0')
    if phil_health == '': phil_health = '0'

    pag_ibig = form.get('pag_ibig', '0')
    if pag_ibig == '': pag_ibig = '0'

    settled_by = form.get('settled_by')

    with mongo.cx.start_session() as session:
        with session.start_transaction():
            accounting = mongo.db.lms_accounting.find_one({
                "branch": ObjectId(branch_id),
            })

            if accounting:
                with decimal.localcontext(D128_CTX):
                    previous_fund_wallet = accounting['total_fund_wallet'] if 'total_fund_wallet' in accounting else Decimal128('0.00')

                    if decimal.Decimal(total_amount_due) > previous_fund_wallet.to_decimal():
                        return jsonify({
                            'status': 'error',
                            'message': "Insufficient fund wallet balance"
                        }), 400
                        
                    new_total_fund_wallet = previous_fund_wallet.to_decimal() - decimal.Decimal(total_amount_due)
                    balance = Decimal128(previous_fund_wallet.to_decimal() - Decimal128(str(total_amount_due)).to_decimal())

                    mongo.db.lms_accounting.update_one({
                        "branch": ObjectId(branch_id)
                    },
                    {'$set': {
                        "total_fund_wallet": Decimal128(new_total_fund_wallet)
                    }},session=session)
            else:
                raise Exception("Likes Error: Accounting data not found")
            
            payslip_doc = mongo.db.lms_payroll_payslips.insert_one({
                'branch': ObjectId(branch_id),
                'employee': ObjectId(employee),
                'position': position,
                'billing_month_from': billing_month_from,
                'billing_month_to': billing_month_to,
                'no_of_days': int(no_of_days),
                'day_off': int(day_off),
                'absent_days': int(absent_days),
                'total_working_days': int(total_working_days),
                'no_of_session': int(no_of_session),
                'salary_rate': Decimal128(salary_rate),
                'total_salary_amount': Decimal128(total_salary_amount),
                'food_allowance': Decimal128(food_allowance),
                'accommodation': Decimal128(accommodation),
                'holiday_pay': Decimal128(holiday_pay),
                'overtime_pay': Decimal128(overtime_pay),
                'month_13_pay': Decimal128(month_13_pay),
                'gross_salary': Decimal128(gross_salary),
                'cash_advance': Decimal128(cash_advance),
                'government_benefits': Decimal128(government_benefits),
                'accommodation_deduction': Decimal128(accommodation_deduction),
                'total_amount_due': Decimal128(total_amount_due),
                'settled_by': settled_by,
                'sss': Decimal128(sss),
                'phil_health': Decimal128(phil_health),
                'pag_ibig': Decimal128(pag_ibig),
                'date': get_date_now(),
            })
            
            mongo.db.lms_fund_wallet_transactions.insert_one({
                'type': 'expenses',
                'running_balance': balance,
                'branch': ObjectId(branch_id),
                'date': get_date_now(),
                'category': 'salary',
                'description': employee,
                'bank_name': '',
                'account_name': '',
                'account_no': '',
                'billing_month_from': billing_month_from,
                'billing_month_to': billing_month_to,
                'qty': None,
                'unit_price': None,
                'total_amount_due': Decimal128(total_amount_due),
                'settled_by': settled_by,
                'remittance': '',
                'sender': '',
                'contact_no': '',
                'address': '',
                'status': None,
                'reference_no': '',
                'employee_information': None,
                'created_at': get_date_now(),
                'created_by': current_user.fname + " " + current_user.lname,
                'payslip': ObjectId(payslip_doc.inserted_id)
            },session=session)
            
    response = {
        'status': 'success',
        'message': "Payslip added successfully!"
    }
    return jsonify(response), 201


@bp_lms.route('/datatables/payroll/payslips', methods=['GET'])
def fetch_payslips_dt():
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    branch_id = request.args.get('branch', '')
    search_value = request.args.get("search[value]")
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    total_records: int
    filtered_records: int
    match = {}
    print(branch_id)
    if branch_id == 'all':
        if current_user.role.name == "Admin":
            pass
        elif current_user.role.name == "Manager":
            match['branch'] = {"$in": [ObjectId(branch) for branch in current_user.branches]}
        elif current_user.role.name == "Partner":
            match['branch'] = {"$in": [ObjectId(branch) for branch in current_user.branches]}
        elif current_user.role.name == "Secretary":
            match['branch'] = current_user.branch.id
    else:
        if current_user.role.name == "Admin":
            match['branch'] = ObjectId(branch_id)
        elif current_user.role.name == "Manager":
            match['branch'] = ObjectId(branch_id)
        elif current_user.role.name == "Partner":
            match['branch'] = ObjectId(branch_id)
        elif current_user.role.name == "Secretary":
            match['branch'] = current_user.branch.id

    if search_value and search_value != '':
        match['employee.lname'] = {'$regex': search_value, '$options' : 'i'}

    # if date_from != "":
    #     match['date'] = {"$gt": convert_to_utc(date_from, 'date_from')}
    
    # if date_to != "":
    #     if 'date' in match:
    #         match['date']['$lt'] = convert_to_utc(date_to, 'date_to')
    #     else:
    #         match['date'] = {'$lt': convert_to_utc(date_to, 'date_to')}

    query = list(mongo.db.lms_payroll_payslips.aggregate([
        {'$lookup': {
            'from': 'auth_users',
            'localField': 'employee',
            'foreignField': '_id',
            'as': 'employee'
        }},
        {"$unwind": {'path': '$employee'}},
        {
            '$lookup': {
                'from': 'lms_branches',
                'localField': 'branch',
                'foreignField': '_id',
                'as': 'branch'
            }
        }, {
            '$unwind': {
                'path': '$branch'
            }
        },
        {'$match': match},
        {"$sort": {
            'date': pymongo.DESCENDING
        }},
        {"$skip": start},
        {"$limit": length},
    ]))
    
    # query = mongo.db.lms_payroll_payslips.find(match).sort('date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_payroll_payslips.find().count()
    filtered_records = len(query)
    table_data = []
    total_ofice_supply = decimal.Decimal(0)

    with decimal.localcontext(D128_CTX):
        for transaction in query:
            transaction_id = str(transaction['_id'])
            transaction_date: datetime = transaction.get('date', None)
            employee = transaction.get('employee', {})
            billing_month_from = transaction.get('billing_month_from', '')
            billing_month_to = transaction.get('billing_month_to', '')
            gross_salary = transaction.get('gross_salary', '0')
            settled_by = transaction.get('settled_by', '')
            total_amount_due = transaction.get('total_amount_due', '0')
            food_allowance = transaction.get('food_allowance', '0')
            accommodation = transaction.get('accommodation', '0')
            cash_advance = transaction.get('cash_advance', '0')
            government_benefits = transaction.get('government_benefits', '0')
            accommodation_deduction = transaction.get('accommodation_deduction', '0')
            branch = transaction.get('branch', {}).get('name', '')

            if accommodation_deduction is None:
                accommodation_deduction = 0
            if government_benefits is None:
                government_benefits = 0
            if cash_advance is None:
                cash_advance = 0
            
            total_deduction = convert_decimal128_to_decimal(cash_advance) + convert_decimal128_to_decimal(government_benefits) \
                + convert_decimal128_to_decimal(accommodation_deduction)

            if transaction_date is None:
                local_datetime = ''
            elif type(transaction_date == datetime):
                local_datetime = transaction_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
            elif type(transaction_date == str):
                to_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                local_datetime = to_date.strftime("%B %d, %Y")
            else: 
                local_datetime = ''
            
            description = employee.get('fname') + " " + employee.get('lname')

            cut_off_date = str(billing_month_from) + " - " + str(billing_month_to)
            # total_ofice_supply = total_ofice_supply + total_amount_due.to_decimal()
            action = """
                <a href="/learning-management/employee/payslip.pdf?payslip_id={}" 
                    style="margin-bottom: 8px;" 
                    type="button" 
                    class="mr-2 btn-icon btn-icon-only btn btn-outline-info btn-print">
                    <i class="pe-7s-print btn-icon-wrapper"> 
                    </i>
                </a>
            """.format(transaction_id)

            table_data.append([
                local_datetime,
                branch,
                description,
                cut_off_date,
                str(gross_salary),
                str(total_deduction),
                str(total_amount_due),
                settled_by,
                action
            ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
        'totalOfficeSupply': str(total_ofice_supply)
    }

    return jsonify(response)


@bp_lms.route('/employee/payslip.pdf')
def print_employee_payslip():
    payslip_id = request.args.get('payslip_id')
    payslip = mongo.db.lms_payroll_payslips.find_one({'_id': ObjectId(payslip_id)})
    employee: User = User.objects.get(id=payslip['employee'])
    gross_salary = payslip.get('gross_salary', '0')
    total_amount_due = payslip.get('total_amount_due', '0')
    food_allowance = payslip.get('food_allowance', '0')
    accommodation = payslip.get('accommodation', '0')
    cash_advance = payslip.get('cash_advance', '0')
    government_benefits = payslip.get('government_benefits', '0')
    accommodation_deduction = payslip.get('accommodation_deduction', '0')
    sss = payslip.get('sss', '0')
    phil_health = payslip.get('phil_health', '0')
    pag_ibig = payslip.get('pag_ibig', '0')
    billing_month_from = payslip.get('billing_month_from', '')
    billing_month_to = payslip.get('billing_month_to', '')
    pay_period = billing_month_from + " - " + billing_month_to
    work_days = payslip.get('total_working_days', '0')
    pay_date = format_utc_to_local(payslip.get('date'))
    salary_rate = payslip.get('salary_rate', '0')

    total_earnings = convert_decimal128_to_decimal(gross_salary)
    total_deduction = convert_decimal128_to_decimal(cash_advance) + convert_decimal128_to_decimal(government_benefits) \
        + convert_decimal128_to_decimal(accommodation_deduction)
    position = payslip.get('position')
    net_amount_in_words = inflect.engine().number_to_words(total_amount_due)

    if position == 'Teacher':
        no_of_session = payslip.get('no_of_session', 0)
        salary =  convert_decimal128_to_decimal(salary_rate) * no_of_session 
        work_days = no_of_session
    else:
        salary =  convert_decimal128_to_decimal(salary_rate) * work_days 

    html = render_template(
        'lms/fund_wallet/pdf_payslip.html',
        employee=employee,
        position=position,
        pay_period=pay_period,
        work_days=work_days,
        pay_date=pay_date,
        total_earnings=format_to_str_php(total_earnings),
        total_deduction=format_to_str_php(total_deduction),
        net_amount=format_to_str_php(total_amount_due),
        net_amount_in_words=net_amount_in_words,
        salary=format_to_str_php(salary),
        sss=format_to_str_php(sss),
        food_allowance=format_to_str_php(food_allowance),
        accommodation=format_to_str_php(accommodation),
        pag_ibig=format_to_str_php(pag_ibig),
        rebate=format_to_str_php(0),
        cash_advance=format_to_str_php(cash_advance),
        phil_health=format_to_str_php(phil_health)
    )
    return html
