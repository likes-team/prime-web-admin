from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from werkzeug.utils import redirect
from prime_home import bp_prime_home
from prime_admin.models import Branch, Registration
from flask import request, jsonify, flash, current_app
from app import mongo, create_app
import pymongo
from prime_admin.models_v2 import StudentV2
from prime_admin.utils.date import format_utc_to_local
from bson.objectid import ObjectId
from app.auth.forms import SendUsAMessageForm
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from datetime import datetime

# pip install google-auth google-auth-oauthlib gspread
import gspread
from google.oauth2.service_account import Credentials


load_dotenv()
config_name = os.getenv('FLASK_ENV')
app = create_app(config_name)

@bp_prime_home.route('/')
def index():
    form = SendUsAMessageForm()

    our_testimonies = list(mongo.db.lms_our_testimonies.find())

    return render_template('prime_home/index.html', form=form,our_testimonies=our_testimonies)


@bp_prime_home.route('/passers')
def passers():
    
    pipeline = [
        {
            '$match': {
                'is_passer': True,
                'no_of_klt': {'$regex': '^KLT-'}  # Filter for no_of_klt that starts with "KLT-"
            }
        },
        {
            '$group': {
                '_id': '$no_of_klt',  # Group by no_of_klt
                'count': {'$sum': 1}  # Count occurrences
            }
        },
        {
            '$sort': {
                '_id': -1  # Sort by no_of_klt in descending order
            }
        }
    ]
    
    results = list(mongo.db.lms_registrations.aggregate(pipeline))

    return render_template('prime_home/passers_page.html', results=results)

@bp_prime_home.route('/passers/', defaults={'klt_number': None})
@bp_prime_home.route('/passers/<string:klt_number>')
def passers_by_klt_number(klt_number):
    if not klt_number:
        return redirect(url_for('prime_home.passers'))
    
    pipeline = [
        {
            '$match': {
                'is_passer': True,
                'no_of_klt': {'$regex': '^KLT-'}  # Filter for no_of_klt that starts with "KLT-"
            }
        },
        {
            '$group': {
                '_id': '$branch',  # Group by branch
                'count': {'$sum': 1}  # Count occurrences
            }
        },
        {
            '$sort': {
                '_id': -1  # Sort by branch in descending order
            }
        }
    ]
    
    query = mongo.db.lms_registrations.aggregate(pipeline)
    data = [doc['_id'] for doc in query]
    branches = list(mongo.db.lms_branches.find({'_id': {"$in": data}}))
    branches_with_teacher = []

    for branch in branches:
            teacher_id = branch.get('teacher', None)
            if teacher_id:
                teacher = mongo.db.auth_users.find_one({'_id': teacher_id})
            else:
                teacher = None

            branches_with_teacher.append({
                'id': branch['_id'],
                'name': branch['name'],
                'teacher': teacher
            })

    return render_template('prime_home/passers_page_by_klt_number.html', klt_number=klt_number, branches=branches_with_teacher)

@bp_prime_home.route('/latest-passers')
def fetch_latest_passers():
    length = 10
    match = {'is_passer': True, 'no_of_klt': {'$regex': '^KLT-'}}
        
    query = mongo.db.lms_registrations.find(match).sort('score', pymongo.DESCENDING).limit(length)
    data = []
    
    for doc in query:
        student = StudentV2(doc)
        
        data.append({
            'name' : student.get_full_name(),
            'score' : student.document.get('score', ''),
        })

    return jsonify(data)

@bp_prime_home.route('/datatables/passers')
def fetch_datatables_passers():
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))

    base_match = {'is_passer': True, 'no_of_klt': request.args.get('klt_number')}

    branch_value = request.args.get('branch')
    if branch_value:
        base_match['branch'] = ObjectId(branch_value)

    full_name_field = {
            "$addFields": {
                "full_name": {
                    "$concat": [
                        {"$ifNull": ["$lname", ""]}, " ",
                        {"$ifNull": ["$mname", ""]}, " ",
                        {"$ifNull": ["$fname", ""]}
                    ]
                }
            }
        }
    pipeline = []

    search_value = request.args.get("search[value]")
    if search_value:
        pipeline.append(full_name_field)
        pipeline.append({
            "$match": {
                **base_match,  # Merge with base_match here
                "full_name": {"$regex": search_value, "$options": "i"}
            }
        })
    else:
        pipeline.append({
            "$match": base_match
        })

    total_records_result = list(mongo.db.lms_registrations.aggregate(pipeline + [{"$count": "count"}]))
    total_records = total_records_result[0]["count"] if total_records_result else 0

    sort_column = 'score'
    sort_direction = pymongo.DESCENDING

    if (request.args.get('order[0][dir]') == 'asc'):
        sort_direction = pymongo.ASCENDING

    if (int(request.args.get('order[0][column]')) == 1):
        sort_column = 'lname'
    elif (int(request.args.get('order[0][column]')) == 2):
        sort_column = 'score'
    else:
        sort_column = 'score'
        sort_direction = pymongo.DESCENDING
    
    pipeline.append({
        "$sort": {sort_column: sort_direction}
    })
    
    pipeline.append({
        "$skip": start
    })
    
    pipeline.append({
        "$limit": length
    })

    query = mongo.db.lms_registrations.aggregate(pipeline)
    table_data = []
    ctr = start

    base_count_pipeline = [{ "$match": base_match }]
    if search_value:
        base_count_pipeline.append(full_name_field)
        base_count_pipeline.append({
            "$match": {
                "full_name": {"$regex": search_value, "$options": "i"}
            }
        })
    
    filtered_records_result = list(mongo.db.lms_registrations.aggregate(base_count_pipeline + [{"$count": "count"}]))
    filtered_records = filtered_records_result[0]["count"] if filtered_records_result else 0
    
    for doc in query:
        student = StudentV2(doc)
        ctr = ctr + 1
        
        table_data.append([
            ctr,
            student.get_full_name(),
            student.document.get('score', ''),
        ])
    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': table_data,
    }
    return jsonify(response)


@bp_prime_home.route('/branches')
def branches():
    return render_template('prime_home/branches_page.html')


@bp_prime_home.route('/testimonies')
def testimonies():
    return render_template('prime_home/testimonies_page.html')


@bp_prime_home.route('/about')
def about():
    return render_template('prime_home/about_page.html')


@bp_prime_home.route('/contact-us')
def contact_us():
    form = SendUsAMessageForm()

    return render_template('prime_home/contact_us_page.html', form=form)

@bp_prime_home.route('/send-us-a-message', methods=['GET', 'POST'])
def send_us_a_message():
    form = SendUsAMessageForm()
    
    if request.method == 'POST':
        if not form.validate_on_submit():
            for key, value in form.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(request.referrer)
        
        # Get form data
        first_name = form.first_name.data
        last_name = form.last_name.data
        age = form.age.data
        address = form.address.data
        email = form.email.data
        contact_number = form.contact_number.data
        message = form.message.data
        subscribe = form.subscribe.data

        # Compose the email message
        msg = Message(
            subject="New Message from Contact Form",
            sender=email,
            recipients=["primekoreanlanguageandreviewce@gmail.com"],
            body=f"""
            You have received a new message from {first_name} {last_name}:

            First Name: {first_name}
            Last Name: {last_name}
            Age: {age}
            Address: {address}
            Email: {email}
            Contact Number: {contact_number}
            Message: {message}

            Subscription Request: {'Yes' if subscribe else 'No'}
            """
        )

        # Send the email
        try:
            mail = Mail(app)
            mail.send(msg)
            flash("Successfully sent the message!", 'success')
        except Exception as e:
            flash(f"Failed to send the message. Error: {e}", 'error')

        # Save data to Google Sheets
        try:
            # Define the scope
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            # Load the service account credentials
            creds = Credentials.from_service_account_file(os.path.join(current_app.root_path, '../primeklc-de737eb8a3b0.json'), scopes=scope)
            client = gspread.authorize(creds)
            # Open the Google Sheet
            sheet = client.open("PrimeKLC - Send us inquiries").sheet1

            current_date = datetime.now().strftime("%m-%d-%Y")

            # Append the data as a new row
            sheet.append_row([
                current_date, first_name, last_name, age, address, email, contact_number, message, 'Yes' if subscribe else 'No'
            ])
        except Exception as e:
            flash(f"Failed to save data to Google Sheets. Error: {e}", 'error')

        return redirect(request.referrer)
    
    return redirect('/')


@bp_prime_home.route('/pre-register', methods=["GET", 'POST'])
def pre_register():
    if request.method == "GET":
        
        branches = Branch.objects

        return render_template(
            'prime_home/pre_register.html',
            branches=branches
        )

    new = Registration()
    new.registration_number = None
    new.full_registration_number = None
    new.schedule = None
    new.branch = Branch.objects.get(id=request.form['branch'])
    new.batch_number = None
    new.contact_person = None
    new.fname = request.form['fname']
    new.mname = request.form['mname']
    new.lname = request.form['lname']
    new.gender = request.form['gender']
    new.suffix = request.form['suffix']
    new.address = request.form['address']
    new.contact_number = request.form['contact_number']
    new.email = request.form['email']
    new.birth_date = request.form['birth_date']
    new.status = "pre_registered"
    new.is_oriented = False

    new.save()

    return redirect(url_for('prime_home.successfully_registered'))

@bp_prime_home.route('/successfully-registered')
def successfully_registered():
    return render_template('prime_home/pre_registered_successfully.html')

