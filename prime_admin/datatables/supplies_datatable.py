import pymongo
from bson import ObjectId
from flask import request, jsonify
from flask_login import current_user
from app import mongo
from prime_admin import bp_lms
from prime_admin.globals import convert_to_utc



@bp_lms.route('/datatables/supplies/monthly-transactions')
def dt_monthly_transactions():
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    filter_year = request.args.get('year', 'all')
    filter_month = request.args.get('month', 'all')
    supplies_type = request.args.get('supplies_type')
    branch_id = request.args.get('branch')
    
    if branch_id == 'all':
        response = {
            'draw': draw,
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
        }
        return jsonify(response)

    total_records: int
    filtered_records: int
        
    _filter = {'branch': ObjectId(branch_id)}
    
    mongo_table = None
    if supplies_type == "office_supplies":
        mongo_table =  mongo.db.lms_office_supplies
    elif supplies_type == "student_supplies":
        mongo_table =  mongo.db.lms_student_supplies

    query = mongo_table.find(_filter).skip(start).limit(length)
    
    table_data = []
    for supply in query:
        one, two, three, four, five = '', '', '', '', ''
        six, seven, eight, nine, ten = '', '', '', '', ''
        eleven, twelve, thirteen, fourteen, fifteen = '', '', '', '', ''
        sixteen, seventeen, eighteen, nineteen, twenty = '', '', '', '', ''
        tone, ttwo, tthree, tfour, tfive = '', '', '', '', ''
        tsix,tseven,teight, tnine, thirty = '', '', '', '', ''
        thone = ''
        
        transactions = supply.get('transactions', [])
        total_used = 0
        
        for trans in transactions:
            date = trans.get('date', None)
            
            if date is None:
                continue
            
            year = date.year
            month = date.month

            if filter_year != "all":
                if year != int(filter_year):
                    continue
                
            if filter_month != "all":
                if month != int(filter_month):
                    continue
            
            quantity = trans.get('quantity', 0)
            if date.day == 1:
                one = quantity
            elif date.day == 2:
                two = quantity
            elif date.day == 3:
                three = quantity
            elif date.day == 4:
                four = quantity
            elif date.day == 5:
                five = quantity
            elif date.day == 6:
                six = quantity
            elif date.day == 7:
                seven = quantity
            elif date.day == 8:
                eight = quantity
            elif date.day == 9:
                nine = quantity
            elif date.day == 10:
                ten = quantity
            elif date.day == 11:
                eleven = quantity
            if date.day == 12:
                twelve = quantity
            elif date.day == 13:
                thirteen = quantity
            if date.day == 14:
                fourteen = quantity
            elif date.day == 15:
                fifteen = quantity
            if date.day == 16:
                sixteen = quantity
            elif date.day == 17:
                seventeen = quantity
            if date.day == 18:
                eighteen = quantity
            elif date.day == 19:
                nineteen = quantity
            if date.day == 20:
                twenty = quantity
            elif date.day == 21:
                tone = quantity
            if date.day == 22:
                ttwo = quantity
            elif date.day == 23:
                tthree = quantity
            if date.day == 24:
                tfour = quantity
            elif date.day == 25:
                tfive = quantity
            elif date.day == 26:
                tsix = quantity
            elif date.day == 27:
                tseven = quantity
            elif date.day == 28:
                teight = quantity
            elif date.day == 29:
                tnine = quantity
            elif date.day == 30:
                thirty = quantity
            elif date.day == 31:
                thone = quantity
            total_used += quantity

        if supplies_type == "office_supplies":
            row = [
                str(supply['_id']),
                supply['description'],
                supply.get('maintaining', ''),
                supply.get('remaining', ''),
                supply.get('uom', ''),
                one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen,fourteen,fifteen,sixteen,seventeen,
                eighteen,nineteen,twenty,tone,ttwo,tthree,tfour,tfive,tsix,tseven,teight,tnine,thirty,thone,
                total_used
            ]
        elif supplies_type == "student_supplies":
            row = [
                str(supply['_id']),
                supply['description'],
                supply.get('completing', ''),
                supply.get('maintaining', ''),
                supply.get('uom', ''),
                one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen,fourteen,fifteen,sixteen,seventeen,
                eighteen,nineteen,twenty,tone,ttwo,tthree,tfour,tfive,tsix,tseven,teight,tnine,thirty,thone,
                total_used
            ]

        table_data.append(row)
        
    total_records = mongo_table.find(_filter).count()
    filtered_records = query.count()

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
    }

    return jsonify(response)


@bp_lms.route('/datatables/supplies/summary')
def dt_summary():
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))
    filter_year = request.args.get('year', 'all')
    filter_month = request.args.get('month', 'all')
    supplies_type = request.args.get('supplies_type')
    branch_id = request.args.get('branch')

    if branch_id == 'all':
        response = {
            'draw': draw,
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
        }
        return jsonify(response)
        
    total_records: int
    filtered_records: int

    _filter = {'branch': ObjectId(branch_id)}
    
    mongo_table = None
    if supplies_type == "office_supplies":
        mongo_table =  mongo.db.lms_office_supplies
    elif supplies_type == "student_supplies":
        mongo_table =  mongo.db.lms_student_supplies
    query = mongo_table.find(_filter).skip(start).limit(length)

    table_data = []
    for supply in query:
        total_used = 0
        transactions = supply.get('transactions', [])

        for trans in transactions:
            quantity = trans.get('quantity', 0)
            date = trans.get('date', None)
            
            if date is None:
                continue
            
            year = date.year
            month = date.month

            if filter_year != "all":
                if year != int(filter_year):
                    continue
                
            if filter_month != "all":
                if month != int(filter_month):
                    continue
            total_used += quantity
                    
        if supplies_type == "office_supplies":
            unit_price = supply.get('price', 0)
            total_price = total_used * unit_price
            
            row = [
                str(supply['_id']),
                supply['description'],
                supply.get('remaining', ''),
                total_used,
                str(unit_price),
                str(total_price)
            ]
        elif supplies_type == "student_supplies":
            row = [
                str(supply['_id']),
                '',
                supply['description'],
                supply.get('remaining', ''),
                total_used
            ]
            
        table_data.append(row)
        
    total_records = mongo_table.find(_filter).count()
    filtered_records = query.count()

    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data,
    }
    return jsonify(response)