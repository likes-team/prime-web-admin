import pymongo
from bson import ObjectId
from mongoengine.queryset.visitor import Q
from flask import abort, jsonify, request
from flask_login import current_user
from app import mongo
from prime_admin import bp_lms
from prime_admin.models import Registration
from prime_admin.models_v2 import StudentV2
from prime_admin.utils.date import format_utc_to_local



@bp_lms.route('/datatables/student-records/hired')
def datatables_student_records_hired():
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    match = {'is_hired': True}
    
    if current_user.role.name == "Admin":
        pass
    elif current_user.role.name == "Manager":
        match['branch'] = {"$in": [ObjectId(branch_id) for branch_id in current_user.branches]}
    elif current_user.role.name == "Partner":
        match['branch'] = {"$in": [ObjectId(branch_id) for branch_id in current_user.branches]}
    elif current_user.role.name == "Secretary":
        match['branch'] = current_user.branch.id

    query = mongo.db.lms_registrations.find(match).sort('added_to_hired_date', pymongo.DESCENDING).skip(start).limit(length)
    total_records = mongo.db.lms_registrations.find(match).count()
    filtered_records = query.count()
    table_data = []
    ctr = start
    
    for doc in query:
        student = StudentV2(doc)
        ctr = ctr + 1
        employer_information = student.document.get('employer_information', {})
        hired_information = student.document.get('hired_information', {})
        current_status = hired_information.get('current_status', None)
        if current_status:
            current_progress = hired_information[current_status].get('current_progress', '')
        else:
            current_progress = ""
        
        table_data.append([
            str(student.get_id()),
            ctr,
            student.document.get('primary_key', ''),
            student.get_full_name(),
            employer_information.get('employer_name', ''),
            employer_information.get('company_name', ''),
            employer_information.get('employer_contact_no', ''),
            employer_information.get('address_in_korea', ''),
            employer_information.get('title_of_work', ''),
            current_progress,
            '',
        ])
    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
    }
    return jsonify(response)


@bp_lms.route('/datatables/student-records/hired/mdl-students', methods=['GET'])
def datatables_student_records_hired_mdl_students():
    if current_user.role.name == "Secretary":
        clients = Registration.objects(Q(status="registered") & Q(is_passer=True)).filter(branch=current_user.branch)
    elif current_user.role.name == "Admin":
        clients = Registration.objects(Q(status="registered") & Q(is_passer=True))
    elif current_user.role.name == "Partner":
        clients = Registration.objects(Q(status="registered") & Q(is_passer=True)).filter(branch__in=current_user.branches)
    elif current_user.role.name == "Manager":
        clients = Registration.objects(Q(status="registered") & Q(is_passer=True)).filter(branch__in=current_user.branches)
    else:
        return abort(404)

    table_data = []
    for client in clients:
        table_data.append([
            str(client.id),
            client.lname,
            client.fname,
            client.mname,
            client.suffix,
            client.contact_number,
            client.status.upper()
        ])
    response = {
        'data': table_data
    }
    return jsonify(response)