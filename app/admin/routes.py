""" MODULE: ADMIN.ROUTES """
from flask import flash, redirect, url_for, request, jsonify
from flask.templating import render_template
from flask_login import login_required, current_user
from flask_cors import cross_origin
from sqlalchemy import text
from app import db, mongo
from app.admin import bp_admin



# @bp_admin.before_request
# def admin_before_request():
#     if current_user.role.name != "Admin":
#         return render_template('auth/authorization_error.html')

@bp_admin.route('/delete/<string:table_name>/<string:oid>',methods=['POST'])
@login_required
def delete(table_name,oid):
    try:
        table_url = request.args.get('table_url')
        query = "DELETE from {} where id = {}".format(table_name,oid)
        db.engine.execute(text(query))
        flash('Deleted Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
        return redirect(request.referrer)
    
    return redirect(url_for(table_url))


@bp_admin.route('/delete-data',methods=["POST"])
@cross_origin()
def delete_data():
    table = request.json['table']
    data = request.json['ids']
    
    try:
        if not data:
            resp = jsonify(result=2)
            resp.headers.add('Access-Control-Allow-Origin', '*')
            resp.status_code = 200
            return resp

        for idx in data:
            query = "DELETE from {} where id = {}".format(table,idx)
            db.engine.execute(text(query))

        resp = jsonify(result=1)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.status_code = 200
        flash('Successfully deleted!','success')

    except Exception as e:
        flash(str(e),'error')
        db.session.rollback()
        resp = jsonify(result=0)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.status_code = 200
    
    return resp
    

@bp_admin.route('/_get_view_modal_data',methods=["GET"])
@cross_origin()
def get_view_modal_data():
    table,column,id = request.args.get('table'),request.args.get('column'), request.args.get('id')
    query = mongo.db[table].find_one({'id': id}, {column: True})
    sql = text(query)
    row = db.engine.execute(sql)
    res = [x[0] if x[0] is not None else '' for x in row]
    resp = jsonify(result=str(res[0]),column=column)
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.status_code = 200
    return resp
