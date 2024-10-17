from flask import jsonify, request
from app import mongo
from prime_admin import bp_lms
from prime_admin.models_v2 import OurTestimoniesV2

@bp_lms.route('/datatables/pages/our_testimonies', methods=['GET'])
def fetch_our_testimonies():
    draw = request.args.get('draw')
    start, length = int(request.args.get('start')), int(request.args.get('length'))

    query = list(mongo.db.lms_our_testimonies.aggregate([
        {"$skip": start},
        {"$limit": length},
    ]))
    total_records = mongo.db.lms_our_testimonies.count()
    filtered_records = len(query)
    table_data = []
    
    for doc in query:
        our_testimony = OurTestimoniesV2(doc)
        table_data.append([
            str(our_testimony.get_id()),
            our_testimony.get_title(),
            'actions'
        ])
        
    response = {
        'draw': draw,
        'recordsTotal': filtered_records,
        'recordsFiltered': total_records,
        'data': table_data
    }
    return jsonify(response)