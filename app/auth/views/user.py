from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from flask_cors import cross_origin
from flask_mongoengine import json
from app import db, mongo
from app.core.models import CoreModel
from app.core.logging import create_log
from app.auth import bp_auth
from app.auth.models import User, UserPermission, Role
from app.auth.forms import UserForm, UserEditForm, UserPermissionForm
from app.auth import auth_urls
from app.auth.permissions import load_permissions, check_create
from app.admin.templating import admin_render_template, admin_table, admin_edit
from bson.objectid import ObjectId



@bp_auth.route('/users')
@login_required
def users():
    # form = UserForm()
    # fields = ['id', 'username', 'fname', 'lname', 'role', 'email']
    # models = [User]

    # _users = User.objects

    # _table_data = []

    # for user in _users:
    #     _table_data.append((
    #         user.id,
    #         user.username,
    #         user.fname,
    #         user.lname,
    #         user.role.name,
    #         user.email
    #     ))
    return render_template('auth/users/users.html', title='Users')


@bp_auth.route('/users/<string:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    try:
        user: User = User.objects.get(id=user_id)

        response = {
            'status': 'success',
            'data': {
                'id': str(user.id),
                'fname': user.fname,
                'lname': user.lname,
                'role': user.role.name,
                'employee_id': user.full_employee_id,
                'username': user.username,
                'email': user.email,
            },
            'message': ""
        }
        return jsonify(response), 200
    except Exception as err:
        print(err)
        return jsonify({
            'status': 'error',
            'message': str(err)
        }), 500


# @bp_auth.route('/get-view-user-data', methods=['GET'])
# @login_required
# def get_view_user_data():
#     _column, _id = request.args.get('column'), request.args.get('id')

#     _data = User.objects(id=_id).values_list(_column)

#     response = jsonify(result=str(_data[0]),column=_column)

#     if _column == "role":
#         response = jsonify(result=str(_data[0].id),column=_column)

#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.status_code = 200
#     return response


@bp_auth.route('/users/create', methods=['POST'])
@login_required
def create_user(**kwargs):

    if not check_create('Users'):
        return render_template("auth/authorization_error.html")

    form = UserForm()

    url = auth_urls['users']

    if 'url' in kwargs:
        url = kwargs.get('url')

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for(url))   

    try:
        user = User()
        
        user.username = form.username.data
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.email = form.email.data if form.email.data != '' else None
        user.role = Role.objects.get(id=form.role.data)
        user.set_password("password")
        user.is_superuser = False
        user.created_by = "{} {}".format(current_user.fname,current_user.lname)
        
        user.save()

        flash('New User Added Successfully!','success')
        create_log("New user added","UserID={}".format(user.id))

        return redirect(url_for(url))

    except Exception as e:
        flash(str(e),'error')
        return redirect(url_for(url))


@bp_auth.route('/users/<string:oid>/edit', methods=['GET', 'POST'])
@login_required
@cross_origin()
def edit_user(oid,**kwargs):
    user = User.objects.get_or_404(id=oid)
    form = UserEditForm(obj=user)

    if request.method == "GET":
        # user_permissions = UserPermission.query.filter_by(user_id=oid).all()
        # form.permission_inline.data = user_permissions

        _scripts = [
            {'bp_auth.static': 'js/auth.js'},
            {'bp_admin.static': 'js/admin_edit.js'}
        ]

        return admin_edit(User, form, auth_urls['edit'], oid, auth_urls['users'],action_template="auth/user_edit_action.html", \
            modals=['auth/user_change_password_modal.html'], scripts=_scripts, **kwargs)
    
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for(auth_urls['users']))
        
    try:
        user.username = form.username.data
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.email = form.email.data if not form.email.data == '' else None
        user.set_updated_at()
        user.updated_by = "{} {}".format(current_user.fname,current_user.lname)

        user.save()
        flash('User update Successfully!','success')
        create_log('User update',"UserID={}".format(oid))

    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for(auth_urls['users']))


@bp_auth.route('/permissions')
@login_required
def user_permission_index():
    fields = [UserPermission.id, User.username, User.fname, CoreModel.name, UserPermission.read, UserPermission.create,
              UserPermission.write, UserPermission.delete]
    model = [UserPermission, User,CoreModel]
    form = UserPermissionForm()
    return admin_table(*model, fields=fields, form=form, list_view_url=auth_urls['user_permission_index'], create_modal=False,
                       view_modal=False, active="Users")


@bp_auth.route('/username_check', methods=['POST'])
def username_check():
    if request.method == 'POST':
        username = request.json['username']
        user = User.objects(username=username).first()
        if user:
            resp = jsonify(result=0)
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(result=1)
            resp.status_code = 200
            return resp


@bp_auth.route('/_email_check',methods=["POST"])
def email_check():
    if request.method == 'POST':
        email = request.json['email']
        user = User.objects(email=email).first()
        if user:
            resp = jsonify(result=0)
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(result=1)
            resp.status_code = 200
            return resp


@bp_auth.route('/change_password/<string:oid>',methods=['POST'])
def change_password(oid):
    user = User.objects.get(id=oid)
    user.set_password(request.form.get('password'))
    
    mongo.db.auth_users.update_one({'_id': ObjectId(oid)},
        {"$set": {
            'password_hash': user.password_hash
        }})

    flash("Password change successfully!",'success')
    return redirect(request.referrer)


@bp_auth.route('/users/<int:oid1>/permissions/<int:oid2>/edit', methods=['POST'])
@cross_origin()
def edit_permission(oid1, oid2):

    permission_type = request.json['permission_type']
    value = request.json['value']

    permission = UserPermission.query.get_or_404(oid2)

    if not permission:
        resp = jsonify(0)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.status_code = 200
        
        return resp

    if permission_type == 'read':
        permission.read = value
    
    elif permission_type == 'create':
        permission.create = value

    elif permission_type == 'write':
        permission.write = value
    
    elif permission_type == "delete":
        permission.delete = value

    db.session.commit()

    load_permissions(current_user.id)

    resp = jsonify(1)
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.status_code = 200

    return resp


@bp_auth.route('/users/get-role-name', methods=['GET'])
@cross_origin()
def get_role_name():
    response = jsonify({
        'roleName': current_user.role.name
    })

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200

    return response