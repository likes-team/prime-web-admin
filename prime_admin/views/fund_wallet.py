import calendar
import pytz
import pymongo
import decimal
from bson import Decimal128
from bson.objectid import ObjectId
from datetime import datetime
from config import TIMEZONE
from flask import jsonify, request
from flask_login import login_required, current_user
from app import mongo
from app.auth.models import User
from app.admin.templating import admin_render_template
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
from prime_admin.utils.currency import convert_decimal128_to_decimal



@bp_lms.route('/fund-wallet')
@login_required
def fund_wallet():
    branches = access.get_current_user_branches()
    payment_options = mongo.db.lms_configurations.find_one({'name': 'payment_options'})['values']
    expenses_categories = mongo.db.lms_configurations.find_one({'name': "expenses_categories"})['values']

    return admin_render_template(
        FundWallet,
        "lms/fund_wallet/fund_wallet.html",
        'learning_management',
        title="Fund Wallet",
        branches=branches,
        payment_options=payment_options,
        expenses_categories=expenses_categories
    )


@bp_lms.route('/branches/<string:branch_id>/add-funds-transactions/dt', methods=['GET'])
def fetch_add_funds_transactions_dt(branch_id):
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    total_records: int
    filtered_records: int
    match = {'type': 'add_fund'}

    if branch_id == 'all':
        total_fund_wallet = 0.00
        
        if current_user.role.name == "Admin":
            pass
        elif current_user.role.name == "Manager":
            match['branch'] = {"$in": current_user.branches}
        elif current_user.role.name == "Partner":
            match['branch'] = {"$in": current_user.branches}
        elif current_user.role.name == "Secretary":
            match['branch'] = current_user.branch.id
    else:
        if current_user.role.name == "Admin":
            match['branch'] = ObjectId(branch_id)
            accounting = mongo.db.lms_accounting.find_one({"branch": ObjectId(branch_id)})
        elif current_user.role.name == "Partner":
            match['branch'] = ObjectId(branch_id)
            accounting = mongo.db.lms_accounting.find_one({"branch": ObjectId(branch_id)})
        elif current_user.role.name == "Manager":
            match['branch'] = ObjectId(branch_id)
            accounting = mongo.db.lms_accounting.find_one({"branch": ObjectId(branch_id)})
        elif current_user.role.name == "Secretary":
            match['branch'] = current_user.branch.id
            accounting = mongo.db.lms_accounting.find_one({"branch": current_user.branch.id})
        total_fund_wallet = accounting['total_fund_wallet'] if 'total_fund_wallet' in accounting else '0.00'

    if date_from != "":
        match['date'] = {"$gt": convert_to_utc(date_from, 'date_from')}
    
    if date_to != "":
        if 'date' in match:
            match['date']['$lt'] = convert_to_utc(date_to, 'date_to')
        else:
            match['date'] = {'$lt': convert_to_utc(date_to, 'date_to')}
     
    query = mongo.db.lms_fund_wallet_transactions.find(match).sort('date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_fund_wallet_transactions.find(match).count()
    filtered_records = query.count()
    
    table_data = []
    
    for transaction in query:
        date = transaction.get('date', None)
        thru = transaction.get('thru', '')
        remittance = transaction.get('remittance', '')
        account_name = transaction.get('account_name', '')
        account_no = transaction.get('account_no', '')
        bank_name = transaction.get('bank_name', '')
        transaction_no = transaction.get('transaction_no', '')
        sender = transaction.get('sender', '')
        receiver = transaction.get('receiver', '')
        amount_received = transaction.get('amount_received', 0.00)
        remarks = transaction.get('remarks', '')
        
        if type(date == datetime):
            local_datetime = date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
        elif type(date == str):
            to_date = datetime.strptime(date, "%Y-%m-%d")
            local_datetime = to_date.strftime("%B %d, %Y")
        else: 
            local_datetime = ''

        table_data.append([
            local_datetime,
            thru,
            bank_name,
            account_name,
            account_no,
            remittance,
            transaction_no,
            sender,
            receiver,
            str(amount_received),
            remarks
        ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
        'totalFundWallet': str(total_fund_wallet)
    }

    return jsonify(response)


@bp_lms.route('/branches/<string:branch_id>/expenses-transactions/dt', methods=['GET'])
def fetch_business_expenses_dt(branch_id):
    year = request.args['year']
    
    business_expenses_service = BusinessExpensesService(branch=branch_id,year=year)
    data = business_expenses_service.get_table()
    response = {
        'data': data,
    }
    return jsonify(response)


@bp_lms.route('/fund-wallet/add-fund', methods=['POST'])
@login_required
def fund_wallet_add_fund():
    form = request.form
    
    try:
        branch_id = form.get('branch')
        thru = form.get('thru', '')
        bank_name = form.get('bank', '')
        remittance = form.get('remittance', '')
        account_name = form.get('account_name', '')
        account_no = form.get('account_no', '')
        transaction_no = form.get('transaction_no', '')
        amount_received = format(float(form.get('amount_received')), '.2f')
        sender = form.get('sender', '')
        receiver = form.get('receiver', '')
        
        with mongo.cx.start_session() as session:
            with session.start_transaction():
                accounting = mongo.db.lms_accounting.find_one({
                    "branch": ObjectId(branch_id),
                })

                if accounting:
                    with decimal.localcontext(D128_CTX):
                        previous_fund_wallet = accounting['total_fund_wallet'] if 'total_fund_wallet' in accounting else Decimal128('0.00')
                        new_total_fund_wallet = previous_fund_wallet.to_decimal() + decimal.Decimal(amount_received)
                        balance = Decimal128(Decimal128(
                            str(accounting["total_fund_wallet"] if 'total_fund_wallet' in accounting else 0.00)).to_decimal() + Decimal128(str(amount_received)).to_decimal())
                        
                        mongo.db.lms_accounting.update_one({
                            "branch": ObjectId(branch_id)
                        },
                        {'$set': {
                            "total_fund_wallet": Decimal128(new_total_fund_wallet)
                        }},session=session)
                else:
                    previous_fund_wallet = Decimal128('0.00')
                    new_total_fund_wallet = decimal.Decimal(amount_received)
                    balance = Decimal128(str(amount_received))

                    mongo.db.lms_accounting.insert_one({
                        "_id": ObjectId(),
                        "branch": ObjectId(branch_id),
                        "active_group": 1,
                        "total_gross_sale": Decimal128("0.00"),
                        "final_fund1": Decimal128("0.00"),
                        "final_fund2": Decimal128("0.00"),
                        "total_fund_wallet": Decimal128(str(amount_received))
                    }, session=session)

                mongo.db.lms_fund_wallet_transactions.insert_one({
                    'type': 'add_fund',
                    'thru': thru,
                    'remittance': remittance,
                    'account_name': account_name,
                    'account_no': account_no,
                    'running_balance': balance,
                    'branch': ObjectId(branch_id),
                    'date': get_date_now(),
                    'bank_name': bank_name,
                    'transaction_no': transaction_no,
                    'sender': sender,
                    'amount_received': Decimal128(amount_received),
                    'receiver': receiver,
                    'previous_total_fund_wallet': previous_fund_wallet,
                    'new_total_fund_wallet': Decimal128(new_total_fund_wallet),
                    'created_at': get_date_now(),
                    'created_by': current_user.fname + " " + current_user.lname
                },session=session)
                
                mongo.db.lms_system_transactions.insert_one({
                    "_id": ObjectId(),
                    "date": get_date_now(),
                    "current_user": current_user.id,
                    "description": "Add fund - transaction no: {}, account no: {}, amount: {}".format(transaction_no, account_no, str(amount_received)),
                    "from_module": "Fund Wallet",
                    'branch': ObjectId(branch_id)
                }, session=session)
        response = {
            'status': 'success',
            'message': "Fund added successfully!"
        }
        return jsonify(response), 201
    except Exception as err:
        return jsonify({
            'status': 'error',
            'message': str(err)
        }), 500


@bp_lms.route('/fund-wallet/add-expenses', methods=['POST'])
@login_required
def fund_wallet_add_expenses():
    form = request.form

    category = form.get('category', '')
    description = form.get('description', '')
    account_no = form.get('account_no', None)
    bank_name = form.get('expenses_bank')
    account_name = form.get('expenses_account_name')
    billing_month_from = form.get('billing_month_from', None)
    billing_month_to = form.get('billing_month_to', None)
    qty = form.get('qty', None)
    unit_price = form.get('unit_price', '0.00')
    if unit_price == '':
        unit_price = '0.00'
    unit_price = format(float(unit_price), '.2f')
    settled_by = form.get('settled_by', '')
    total_amount_due = format(float(form.get('total_amount_due', '0.00')), '.2f')
    branch_id = form.get('branch', None)
    remittance = form.get('expenses_remittance')
    sender = form.get('expenses_sender')
    contact_no = form.get('expenses_contact_no')
    address = form.get('expenses_address')
    cut_off = form.get('cut_off')
    remarks = form.get('expenses_remarks')

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

            status = None
            reference_no = None
            employee_information = None
            
            if category == "office_supply":
                InventoryService.inbound_office_supply(description, branch_id, qty, unit_price, session=session)
            elif category == "rebates":
                if remittance == "OVER THE COUNTER":
                    status = "PROCESSED"
                    reference_no = "OVER THE COUNTER"
                else:
                    status = "PROCESSING"

                mongo.db.lms_registration_payments.update_many({
                    'contact_person': ObjectId(description),
                    'branch': ObjectId(branch_id),
                    'is_expenses': False
                }, {'$set': {
                    'is_expenses': True
                }}, session=session)
            elif category == 'Bookeeper':
                query = mongo.db.auth_users.find_one({'_id': ObjectId(description)})
                employee_information = query.get('employee_information')

            mongo.db.lms_fund_wallet_transactions.insert_one({
                'type': 'expenses',
                'running_balance': balance,
                'branch': ObjectId(branch_id),
                'date': get_date_now(),
                'category': category,
                'description': description,
                'bank_name': bank_name,
                'account_name': account_name,
                'account_no': account_no,
                'billing_month_from': billing_month_from,
                'billing_month_to': billing_month_to,
                'qty': qty,
                'unit_price': unit_price,
                'total_amount_due': Decimal128(total_amount_due),
                'settled_by': settled_by,
                'remittance': remittance,
                'sender': sender,
                'contact_no': contact_no,
                'address': address,
                'status': status,
                'reference_no': reference_no,
                'employee_information': employee_information,
                'cut_off': cut_off,
                'remarks': remarks,
                'created_at': get_date_now(),
                'created_by': current_user.fname + " " + current_user.lname
            },session=session)
            
            mongo.db.lms_system_transactions.insert_one({
                "_id": ObjectId(),
                "date": get_date_now(),
                "current_user": current_user.id,
                "description": "Add expenses - description: {}, category: {}, amount: {}".format(description, category, str(total_amount_due)),
                "from_module": "Fund Wallet",
                'branch': ObjectId(branch_id)
            }, session=session)
    response = {
        'status': 'success',
        'message': "Expenses added successfully!"
    }
    return jsonify(response), 201


@bp_lms.route('/fund-wallet/list-of-earnings')
def get_list_of_earnings():
    contact_person_id = request.args['contact_person']
    branch_id = request.args['branch']
    marketer: User = User.objects.get(id=contact_person_id)
    service = PaymentService.find_payments(
        PaymentQueryFilter(
            contact_person=contact_person_id,
            branch=branch_id,
            status='approved',
            is_expenses=False
        )
    )
    payments = service.get_data()
    table_data = []
    html_status = """<div class="text-center mb-2 mr-2 badge badge-pill badge-success">APPROVED</div>"""

    for payment in payments:
        payment: PaymentV2
        table_data.append([
            str(payment.student.get_id()),
            str(payment.get_id()),
            marketer.full_name,
            payment.student.get_full_name(),
            payment.student.batch_no.get_no() if payment.student.batch_no is not None else '',
            payment.get_earnings(currency=True),
            payment.student.schedule,
            payment.student.get_payment_mode(),
            html_status,
        ])
    response = {
        'data': table_data,
    }
    return jsonify(response)


@bp_lms.route('/branches/<string:branch_id>/salary/dt', methods=['GET'])
def fetch_salary_dt(branch_id):
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    total_records: int
    filtered_records: int
    match = {'category': {'$in': ['salary', 'salary_and_rebates']}}
    search_value = request.args.get("search[value]")

    if branch_id == 'all':
        if current_user.role.name == "Admin":
            pass
        elif current_user.role.name == "Manager":
            match['branch'] = {"$in": current_user.branches}
        elif current_user.role.name == "Partner":
            match['branch'] = {"$in": current_user.branches}
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

    # if date_from != "":
    #     match['date'] = {"$gt": convert_to_utc(date_from, 'date_from')}
    
    # if date_to != "":
    #     if 'date' in match:
    #         match['date']['$lt'] = convert_to_utc(date_to, 'date_to')
    #     else:
    #         match['date'] = {'$lt': convert_to_utc(date_to, 'date_to')}
    filter_employee = {}
    if search_value != "":
        filter_employee['employee.lname'] = {"$regex": search_value, '$options' : 'i'}

    query = list(mongo.db.lms_fund_wallet_transactions.aggregate([
        {"$match": match},
        {"$addFields": {"descriptionObjectId": {"$toObjectId": "$description"}}},
        {"$lookup": {"from": "auth_users", "localField": "descriptionObjectId",
                        "foreignField": "_id", 'as': "employee"}},
        {"$unwind": {"path": '$employee'}},
        {"$match": filter_employee},
        {"$lookup": {"from": "lms_payroll_payslips", "localField": "payslip",
                        "foreignField": "_id", 'as': "payslip"}},
        {"$unwind": {"path": '$payslip'}},
        {"$sort": {
            'date': pymongo.DESCENDING
        }},
        {"$skip": start},
        {"$limit": length},
    ]))
    filtered_records = len(query)

    if search_value != "":
        total_records = len(query)
    else:
        total_records = mongo.db.lms_fund_wallet_transactions.find(match).count()
    
    table_data = []
    total_ofice_supply = decimal.Decimal(0) 
    
    with decimal.localcontext(D128_CTX):
        for transaction in query:
            transaction_date: datetime = transaction.get('date', None)
            description = transaction.get('description', '')
            billing_month_from = transaction.get('billing_month_from', '')
            billing_month_to = transaction.get('billing_month_to', '')
            settled_by = transaction.get('settled_by', '')
            total_amount_due = transaction.get('total_amount_due', 0.00)
            
            cash_advance = transaction['payslip']['cash_advance']
            government_benefits = transaction['payslip']['government_benefits']
            accommodation_deduction = transaction['payslip']['accommodation_deduction']
            gross_salary = transaction['payslip']['gross_salary']

            if accommodation_deduction is None:
                accommodation_deduction = 0
            if government_benefits is None:
                government_benefits = 0
            if cash_advance is None:
                cash_advance = 0

            total_deduction = convert_decimal128_to_decimal(cash_advance) + convert_decimal128_to_decimal(government_benefits) \
                + convert_decimal128_to_decimal(accommodation_deduction)

            if type(transaction_date == datetime):
                local_datetime = transaction_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
            elif type(transaction_date == str):
                to_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                local_datetime = to_date.strftime("%B %d, %Y")
            else: 
                local_datetime = ''
        
            if search_value != '':
                description = \
                    transaction['employee']['fname'] + " " + transaction['employee']['lname']
            else:
                contact_person : User = User.objects.get(id=description)
                description = contact_person.full_name

            cut_off_date = str(billing_month_from) + " - " + str(billing_month_to)
            # total_ofice_supply = total_ofice_supply + total_amount_due.to_decimal()

            table_data.append([
                local_datetime,
                description,
                cut_off_date,
                str(gross_salary),
                str(cash_advance),
                str(accommodation_deduction),
                str(government_benefits),
                str(total_deduction),
                str(total_amount_due),
                settled_by,
            ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
        'totalOfficeSupply': str(total_ofice_supply)
    }

    return jsonify(response)


@bp_lms.route('/branches/<string:branch_id>/rebate/dt', methods=['GET'])
def fetch_rebate_dt(branch_id):
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    total_records: int
    filtered_records: int
    filter: dict

    if branch_id == 'all':
        if current_user.role.name == "Admin":
            filter = {'category': 'rebates'}
        elif current_user.role.name == "Partner":
            filter = {'category': 'rebates', 'branch': {"$in": current_user.branches}}
        elif current_user.role.name == "Secretary":
            filter = {'category': 'rebates','branch': current_user.branch.id}
    else:
        if current_user.role.name == "Secretary":
            filter = {'category': 'rebates', 'branch': current_user.branch.id}
        elif current_user.role.name == "Admin":
            filter = {'category': 'rebates', 'branch': ObjectId(branch_id)}
        elif current_user.role.name == "Partner":
            filter = {'category': 'rebates', 'branch': ObjectId(branch_id)}

    # if date_from != "":
    #     filter['date'] = {"$gt": convert_to_utc(date_from, 'date_from')}
    
    # if date_to != "":
    #     if 'date' in filter:
    #         filter['date']['$lt'] = convert_to_utc(date_to, 'date_to')
    #     else:
    #         filter['date'] = {'$lt': convert_to_utc(date_to, 'date_to')}
     
    query = mongo.db.lms_fund_wallet_transactions.find(filter).sort('date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_fund_wallet_transactions.find(filter).count()
    filtered_records = query.count()
    
    table_data = []
    
    total_ofice_supply = decimal.Decimal(0)
    
    with decimal.localcontext(D128_CTX):
        for transaction in query:
            transaction_date: datetime = transaction.get('date', None)
            description = transaction.get('description', '')
            billing_month_from = transaction.get('billing_month_from', '')
            billing_month_to = transaction.get('billing_month_to', '')
            settled_by = transaction.get('settled_by', '')
            total_amount_due = transaction.get('total_amount_due', 0.00)
        
            if type(transaction_date == datetime):
                local_datetime = transaction_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
            elif type(transaction_date == str):
                to_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                local_datetime = to_date.strftime("%B %d, %Y")
            else: 
                local_datetime = ''
            
            month_index = transaction_date.month
            
            contact_person : User = User.objects.get(id=description)
            description = contact_person.full_name
            
            cut_off_date = str(billing_month_from) + " - " + str(billing_month_to)
            # total_ofice_supply = total_ofice_supply + total_amount_due.to_decimal()

            table_data.append([
                local_datetime,
                description,
                cut_off_date,
                str(total_amount_due),
                '',
                str(total_amount_due),
                settled_by,
            ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
        'totalOfficeSupply': str(total_ofice_supply)
    }

    return jsonify(response)


@bp_lms.route('/branches/<string:branch_id>/other-expenses/dt', methods=['GET'])
def fetch_other_expenses_dt(branch_id):
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    total_records: int
    filtered_records: int
    match = {'category': 'other_expenses'}

    if branch_id == 'all':
        if current_user.role.name == "Admin":
            pass
        elif current_user.role.name == "Manager":
            match['branch'] = {"$in": current_user.branches}
        elif current_user.role.name == "Partner":
            match['branch'] = {"$in": current_user.branches}
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

    # if date_from != "":
    #     match['date'] = {"$gt": convert_to_utc(date_from, 'date_from')}
    
    # if date_to != "":
    #     if 'date' in match:
    #         match['date']['$lt'] = convert_to_utc(date_to, 'date_to')
    #     else:
    #         match['date'] = {'$lt': convert_to_utc(date_to, 'date_to')}
     
    query = mongo.db.lms_fund_wallet_transactions.find(match).sort('date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_fund_wallet_transactions.find(match).count()
    filtered_records = query.count()
    
    table_data = []
    
    total_ofice_supply = decimal.Decimal(0)
    
    with decimal.localcontext(D128_CTX):
        for transaction in query:
            transaction_date: datetime = transaction.get('date', None)
            description = transaction.get('description', '')
            billing_month_from = transaction.get('billing_month_from', '')
            billing_month_to = transaction.get('billing_month_to', '')
            settled_by = transaction.get('settled_by', '')
            total_amount_due = transaction.get('total_amount_due', 0.00)
        
            if type(transaction_date == datetime):
                local_datetime = transaction_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
            elif type(transaction_date == str):
                to_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                local_datetime = to_date.strftime("%B %d, %Y")
            else: 
                local_datetime = ''
            
            # total_ofice_supply = total_ofice_supply + total_amount_due.to_decimal()

            table_data.append([
                local_datetime,
                description,
                str(total_amount_due),
                settled_by,
            ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
    }

    return jsonify(response)


@bp_lms.route('/branches/<string:branch_id>/refund/dt', methods=['GET'])
def fetch_refund_dt(branch_id):
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    total_records: int
    filtered_records: int
    match = {'category': 'refund'}

    if branch_id == 'all':
        if current_user.role.name == "Admin":
            pass
        elif current_user.role.name == "Manager":
            match['branch'] = {"$in": current_user.branches}
        elif current_user.role.name == "Partner":
            match['branch'] = {"$in": current_user.branches}
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

    # if date_from != "":
    #     filter['date'] = {"$gt": convert_to_utc(date_from, 'date_from')}
    
    # if date_to != "":
    #     if 'date' in filter:
    #         filter['date']['$lt'] = convert_to_utc(date_to, 'date_to')
    #     else:
    #         filter['date'] = {'$lt': convert_to_utc(date_to, 'date_to')}
     
    query = mongo.db.lms_fund_wallet_transactions.find(match).sort('date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_fund_wallet_transactions.find(match).count()
    filtered_records = query.count()
    table_data = []
    total_ofice_supply = decimal.Decimal(0)
    
    with decimal.localcontext(D128_CTX):
        for transaction in query:
            transaction_date: datetime = transaction.get('date', None)
            description = transaction.get('description', '')
            billing_month_from = transaction.get('billing_month_from', '')
            billing_month_to = transaction.get('billing_month_to', '')
            settled_by = transaction.get('settled_by', '')
            total_amount_due = transaction.get('total_amount_due', 0.00)
        
            if type(transaction_date == datetime):
                local_datetime = transaction_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
            elif type(transaction_date == str):
                to_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                local_datetime = to_date.strftime("%B %d, %Y")
            else: 
                local_datetime = ''
            
            student: Registration = Registration.objects.get(id=description)

            # total_ofice_supply = total_ofice_supply + total_amount_due.to_decimal()
            books = 'None'
            uniforms = 'None'
            id_materials = 'None'

            if student.books:
                if student.books['volume1']:
                    books = "Vol. 1"
                if student.books['volume2']:
                    books += " Vol. 2"
                if student.books['book_none']:
                    books = "None"
            else:
                books = "None"

            if student.uniforms:
                if student.uniforms['uniform_none']:
                    uniforms = "None"
                elif student.uniforms['uniform_xs']:
                    uniforms = "XS"
                elif student.uniforms['uniform_s']:
                    uniforms = "S"
                elif student.uniforms['uniform_m']:
                    uniforms = "M"
                elif student.uniforms['uniform_l']:
                    uniforms = "L"
                elif student.uniforms['uniform_xl']:
                    uniforms = "XL"
                elif student.uniforms['uniform_xxl']:
                    uniforms = "XXL"
            else:
                uniforms = "None"

            if student.id_materials:
                if student.id_materials['id_card']:
                    id_materials = "ID Card"
                if student.id_materials['id_lace']:
                    id_materials += " ID Lace"
            else:
                id_materials = "None"

            table_data.append([
                local_datetime,
                student.full_name,
                student.full_registration_number,
                student.batch_number.number,
                student.schedule,
                str(total_amount_due),
                books,
                uniforms,
                id_materials,
                student.contact_person.full_name,
                str(student.fle),
            ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
    }
    return jsonify(response)


@bp_lms.route('/branches/<string:branch_id>/employee-benefits/dt', methods=['GET'])
def fetch_employee_benefits_dt(branch_id):
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    total_records: int
    filtered_records: int
    match = {'category': 'Bookeeper'}

    if branch_id == 'all':
        if current_user.role.name == "Admin":
            pass
        elif current_user.role.name == "Manager":
            match['branch'] = {"$in": current_user.branches}
        elif current_user.role.name == "Partner":
            match['branch'] = {"$in": current_user.branches}
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

    query = mongo.db.lms_fund_wallet_transactions.find(match).sort('date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_fund_wallet_transactions.find(match).count()
    filtered_records = query.count()
    table_data = []
    total_ofice_supply = decimal.Decimal(0)
    
    with decimal.localcontext(D128_CTX):
        for transaction in query:
            transaction_date: datetime = transaction.get('date', None)
            description = transaction.get('description')
            billing_month_from = transaction.get('billing_month_from', '')
            billing_month_to = transaction.get('billing_month_to', '')
            settled_by = transaction.get('settled_by', '')
            total_amount_due = transaction.get('total_amount_due', 0.00)
            employee_information = transaction.get('employee_information')
            ee = employee_information.get('ee')
            er = employee_information.get('er')
            ee_sss = convert_decimal128_to_decimal(ee.get('sss', 0))
            ee_phil = convert_decimal128_to_decimal(ee.get('phil', 0))
            ee_pag_ibig = convert_decimal128_to_decimal(ee.get('pag_ibig', 0))
            er_sss = convert_decimal128_to_decimal(er.get('sss', 0))
            er_phil = convert_decimal128_to_decimal(er.get('phil', 0))
            er_pag_ibig = convert_decimal128_to_decimal(er.get('pag_ibig', 0))
            total_ee = ee_sss + ee_phil + ee_pag_ibig
            total_er = er_sss + er_phil + er_pag_ibig
            employee = mongo.db.auth_users.find_one({'_id': ObjectId(description)})
        
            if type(transaction_date == datetime):
                local_datetime = transaction_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
            elif type(transaction_date == str):
                to_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                local_datetime = to_date.strftime("%B %d, %Y")
            else: 
                local_datetime = ''
            
            table_data.append([
                local_datetime,
                employee['fname'] + " " + employee['lname'],
                billing_month_from + " - " + billing_month_to,
                str(ee.get('sss')),
                str(ee.get('pag_ibig')),
                str(ee.get('phil')),
                str(total_ee),
                str(er.get('sss')),
                str(er.get('pag_ibig')),
                str(er.get('phil')),
                str(total_er),
                str(total_amount_due),
            ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
    }
    return jsonify(response)


@bp_lms.route('/branches/<string:branch_id>/bir/dt', methods=['GET'])
def fetch_bir_dt(branch_id):
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    total_records: int
    filtered_records: int
    filter: dict

    if branch_id == 'all':
        if current_user.role.name == "Admin":
            filter = {'category': 'BIR'}
        elif current_user.role.name == "Partner":
            filter = {'category': 'BIR', 'branch': {"$in": current_user.branches}}
        elif current_user.role.name == "Secretary":
            filter = {'category': 'BIR','branch': current_user.branch.id}
    else:
        if current_user.role.name == "Secretary":
            filter = {'category': 'BIR', 'branch': current_user.branch.id}
        elif current_user.role.name == "Admin":
            filter = {'category': 'BIR', 'branch': ObjectId(branch_id)}
        elif current_user.role.name == "Partner":
            filter = {'category': 'BIR', 'branch': ObjectId(branch_id)}

    # if date_from != "":
    #     filter['date'] = {"$gt": convert_to_utc(date_from, 'date_from')}
    
    # if date_to != "":
    #     if 'date' in filter:
    #         filter['date']['$lt'] = convert_to_utc(date_to, 'date_to')
    #     else:
    #         filter['date'] = {'$lt': convert_to_utc(date_to, 'date_to')}
     
    query = mongo.db.lms_fund_wallet_transactions.find(filter).sort('date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_fund_wallet_transactions.find(filter).count()
    filtered_records = query.count()
    
    table_data = []
    with decimal.localcontext(D128_CTX):
        for transaction in query:
            transaction_date: datetime = transaction.get('date', None)
            description = transaction.get('description', '')
            account_no = transaction.get('account_no', '')
            settled_by = transaction.get('settled_by', '')
            total_amount_due = transaction.get('total_amount_due', 0.00)
        
            if type(transaction_date == datetime):
                local_datetime = transaction_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
            elif type(transaction_date == str):
                to_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                local_datetime = to_date.strftime("%B %d, %Y")
            else: 
                local_datetime = ''
            
            table_data.append([
                local_datetime,
                description,
                account_no,
                str(total_amount_due),
                settled_by,
            ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
    }
    return jsonify(response)


@bp_lms.route('/branches/<string:branch_id>/business-permit/dt', methods=['GET'])
def fetch_business_permit_dt(branch_id):
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    total_records: int
    filtered_records: int
    filter: dict

    if branch_id == 'all':
        if current_user.role.name == "Admin":
            filter = {'category': 'Business Permit'}
        elif current_user.role.name == "Partner":
            filter = {'category': 'Business Permit', 'branch': {"$in": current_user.branches}}
        elif current_user.role.name == "Secretary":
            filter = {'category': 'Business Permit','branch': current_user.branch.id}
    else:
        if current_user.role.name == "Secretary":
            filter = {'category': 'Business Permit', 'branch': current_user.branch.id}
        elif current_user.role.name == "Admin":
            filter = {'category': 'Business Permit', 'branch': ObjectId(branch_id)}
        elif current_user.role.name == "Partner":
            filter = {'category': 'Business Permit', 'branch': ObjectId(branch_id)}

    # if date_from != "":
    #     filter['date'] = {"$gt": convert_to_utc(date_from, 'date_from')}
    
    # if date_to != "":
    #     if 'date' in filter:
    #         filter['date']['$lt'] = convert_to_utc(date_to, 'date_to')
    #     else:
    #         filter['date'] = {'$lt': convert_to_utc(date_to, 'date_to')}
     
    query = mongo.db.lms_fund_wallet_transactions.find(filter).sort('date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_fund_wallet_transactions.find(filter).count()
    filtered_records = query.count()
    
    table_data = []
    with decimal.localcontext(D128_CTX):
        for transaction in query:
            transaction_date: datetime = transaction.get('date', None)
            description = transaction.get('description', '')
            account_no = transaction.get('account_no', '')
            settled_by = transaction.get('settled_by', '')
            total_amount_due = transaction.get('total_amount_due', 0.00)
        
            if type(transaction_date == datetime):
                local_datetime = transaction_date.replace(tzinfo=pytz.utc).astimezone(TIMEZONE).strftime("%B %d, %Y")
            elif type(transaction_date == str):
                to_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                local_datetime = to_date.strftime("%B %d, %Y")
            else: 
                local_datetime = ''
            
            table_data.append([
                local_datetime,
                description,
                account_no,
                str(total_amount_due),
                settled_by,
            ])

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
    }
    return jsonify(response)


@bp_lms.route('api/supplies', methods=['GET'])
def get_supplies():
    branch_id = request.args.get('branch')
    if branch_id == 'all':
        match = {}
    else:
        match = {'branch': ObjectId(branch_id)}
        
    query = mongo.db.lms_office_supplies.find(match)
    list_supplies = []
    list_supplies_ids = []
    
    for row in query:
        if row['description'] in list_supplies_ids:
            # Prevent duplicates
            continue
        
        list_supplies_ids.append(row['description'])
        list_supplies.append({
            'id': str(row['_id']),
            'description': row['description'],
        })

    return jsonify({
        'status': 'success',
        'data': list_supplies,
        'message': ""
    }), 200
    

@bp_lms.route('api/supplies/<string:description>', methods=['GET'])
def get_supply(description):
    query = mongo.db.lms_office_supplies.find_one({'description': description})

    if query is None:
        return jsonify({'status': 'error'}), 200

    product = {
        'id': str(query['_id']),
        'description': query['description'],
        'price': str(query.get('price', 0))
    }
    
    return jsonify({
        'status': 'success',
        'data': product,
        'message': ""
    }), 200
    

@bp_lms.route('employees/<string:employee_id>/get-government-benefits', methods=['GET'])
def get_goverment_benefits(employee_id):
    query = mongo.db.auth_users.find_one({'_id': ObjectId(employee_id)})
    employee_information = query.get('employee_information')
    
    if employee_information is None:
        return jsonify({'status': 'error', 'message': "Government benefits is not set"}), 200
    
    ee = employee_information.get('ee')
    er = employee_information.get('er')
    ee_sss = convert_decimal128_to_decimal(ee.get('sss', 0))
    ee_phil = convert_decimal128_to_decimal(ee.get('phil', 0))
    ee_pag_ibig = convert_decimal128_to_decimal(ee.get('pag_ibig', 0))
    er_sss = convert_decimal128_to_decimal(er.get('sss', 0))
    er_phil = convert_decimal128_to_decimal(er.get('phil', 0))
    er_pag_ibig = convert_decimal128_to_decimal(er.get('pag_ibig', 0))
    
    total_ee = ee_sss + ee_phil + ee_pag_ibig
    total_er = er_sss + er_phil + er_pag_ibig
    total = str(total_ee + total_er)
    return jsonify({'status': 'success', 'data': {'total': total}})    
    

@bp_lms.route('/fetch-other-expenses-items', methods=['GET'])
def fetch_other_expenses_items():
    query = mongo.db.lms_other_expenses_items.find({})
    
    items_list = []
    
    for row in query:
        items_list.append({
            'id': str(row['_id']),
            'description': row['description']
        })
        
    return jsonify({
        'status': 'success',
        'data': items_list
    }), 200
    

@bp_lms.route('/fetch-bookeeper-items', methods=['GET'])
def fetch_bookeeper_items():
    category = request.args.get('category')
    query = mongo.db.lms_bookeeper_items.find_one({'category': category})
    
    items_list = []
    for row in query['items']:
        items_list.append({
             'description': row['description']
        })
        
    return jsonify({
        'status': 'success',
        'data': items_list
    })
    
    
@bp_lms.route('/fetch-employees')
def fetch_employees():
    branch = request.args.get('branch')
    position = request.args.get('position')
    employees = get_employees(position, branch_id=branch)
    data = []

    for employee in employees:
        data.append({
            'id': str(employee.id),
            'full_name': employee.full_name
        })
    response = {
        'data': data
    }
    return jsonify(response)


@bp_lms.route('/fetch-students')
def fetch_students():
    branch = request.args.get('branch')
    service = StudentService.find_students(StudentQueryFilter(
        branch=branch,
        sort={'lname': pymongo.ASCENDING}
    ))
    students = service.get_data()
    data = []
    
    for student in students:
        student: StudentV2
        data.append({
            'full_name': student.get_full_name(reverse=True)
        })
    response = {
        'data': data
    }
    return jsonify(response)
