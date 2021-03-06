import decimal
from prime_admin.globals import get_date_now
from flask.json import jsonify
from app.auth.models import Role, User
from prime_admin.forms import InventoryForm, PartnerForm, SecretaryEditForm, SecretaryForm, StudentForm, TeacherForm, TrainingCenterEditForm, TrainingCenterForm
from flask_login import login_required, current_user
from app.admin.templating import admin_render_template, admin_table, admin_edit
from prime_admin import bp_lms
from prime_admin.models import Branch, Equipment, InboundOutbound, Inventory, Secretary, Supplies, Utilities
from flask import redirect, url_for, request, current_app, flash
from app import db
from datetime import datetime
from config import TIMEZONE



@bp_lms.route('/equipments')
@login_required
def equipments():
    form = InventoryForm()
    form.__heading__ = "Equipments"

    _table_data = []

    _equipments = Inventory.objects(type="equipment")

    for equipment in _equipments:
        _table_data.append((
            equipment.id,
            equipment.maintaining,
            equipment.description,
            equipment.released,
            equipment.remaining,
            equipment.total_replacement,
        ))

    return admin_table(
        Equipment,
        fields=[],
        form=form,
        table_data=_table_data,
        create_url='lms.create_equipment',
        edit_url='lms.edit_secretary',
        view_modal_url='/learning-management/get-view-equipment-data'
        )


@bp_lms.route('/get-view-equipment-data', methods=['GET'])
@login_required
def get_view_equipment_data():
    _column, _id = request.args.get('column'), request.args.get('id')

    _data = Inventory.objects(id=_id).values_list(_column)

    try:
        _data = Inventory.objects(id=_id).values_list(_column)

        if _data[0] is None:
            response = jsonify(result='',column=_column)
        else:
            response = jsonify(result=str(_data[0]),column=_column)

    except Exception:
        pass

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200
    return response


@bp_lms.route('/equipments/create',methods=['GET','POST'])
@login_required
def create_equipment():
    form = InventoryForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('lms.equipments'))

    try:
        equipment = Inventory()

        equipment.description = form.description.data
        equipment.maintaining = form.maintaining.data if form.maintaining.data != '' else None
        equipment.remaining = form.remaining.data if form.remaining.data != '' else None
        equipment.type = "equipment"

        equipment.created_by = "{} {}".format(current_user.fname,current_user.lname)

        equipment.save()

        flash('New Equipment Added Successfully!','success')

    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('lms.equipments'))



@bp_lms.route('/supplies')
@login_required
def supplies():
    form = InventoryForm()
    form.__heading__ = "Supplies"

    _table_data = []

    _equipments = Inventory.objects(type="supplies")

    for equipment in _equipments:
        one, two, three, four, five = '', '', '', '', ''
        six, seven, eight, nine, ten = '', '', '', '', ''
        eleven, twelve, thirteen, fourteen, fifteen = '', '', '', '', ''
        sixteen, seventeen, eighteen, nineteen, twenty = '', '', '', '', ''
        tone, ttwo, tthree, tfour, tfive = '', '', '', '', ''
        tsix,tseven,teight, tnine, thirty = '', '', '', '', ''
        thone = ''

        for x in equipment.transactions:
            if x.date is None:
                continue

            if x.date.day == 1:
                one = x.quantity
            elif x.date.day == 2:
                two = x.quantity
            elif x.date.day == 3:
                three = x.quantity
            elif x.date.day == 4:
                four = x.quantity
            elif x.date.day == 5:
                five = x.quantity
            elif x.date.day == 6:
                six = x.quantity
            elif x.date.day == 7:
                seven = x.quantity
            elif x.date.day == 8:
                eight = x.quantity
            elif x.date.day == 9:
                nine = x.quantity
            elif x.date.day == 10:
                ten = x.quantity
            elif x.date.day == 11:
                eleven = x.quantity
            if x.date.day == 12:
                twelve = x.quantity
            elif x.date.day == 13:
                thirteen = x.quantity
            if x.date.day == 14:
                fourteen = x.quantity
            elif x.date.day == 15:
                fifteen = x.quantity
            if x.date.day == 16:
                sixteen = x.quantity
            elif x.date.day == 17:
                seventeen = x.quantity
            if x.date.day == 18:
                eighteen = x.quantity
            elif x.date.day == 19:
                nineteen = x.quantity
            if x.date.day == 20:
                twenty = x.quantity
            elif x.date.day == 21:
                tone = x.quantity
            if x.date.day == 22:
                ttwo = x.quantity
            elif x.date.day == 23:
                tthree = x.quantity
            if x.date.day == 24:
                tfour = x.quantity
            elif x.date.day == 25:
                tfive = x.quantity
            elif x.date.day == 26:
                tsix = x.quantity
            elif x.date.day == 27:
                tseven = x.quantity
            elif x.date.day == 28:
                teight = x.quantity
            elif x.date.day == 29:
                tnine = x.quantity
            elif x.date.day == 30:
                thirty = x.quantity
            elif x.date.day == 31:
                thone = x.quantity
        
        _table_data.append((
            equipment.id,
            "actions",
            equipment.description,
            equipment.uom, equipment.qty,
            equipment.maintaining,
            one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen,fourteen,fifteen,sixteen,seventeen,
            eighteen,nineteen,twenty,tone,ttwo,tthree,tfour,tfive,tsix,tseven,teight,tnine,thirty,thone,
            equipment.released,
            equipment.remaining,
            equipment.total_replacement,
            equipment.price,
            '',
        ))

    return admin_table(
        Supplies,
        fields=[],
        form=form,
        table_template="lms/supplies_table.html",
        table_data=_table_data,
        create_url='lms.create_supplies',
        edit_url=False,
        modals=['lms/inbound_modal.html', 'lms/outbound_modal.html'],  
        scripts=[],
        view_modal=False,
        # view_modal_url='/learning-management/get-view-supplies-data'
        )


@bp_lms.route('/get-view-supplies-data', methods=['GET'])
@login_required
def get_view_supplies_data():
    _column, _id = request.args.get('column'), request.args.get('id')

    _data = Inventory.objects(id=_id).values_list(_column)

    response = jsonify(result=str(_data[0]),column=_column)

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200
    return response


@bp_lms.route('/supplies/create',methods=['GET','POST'])
@login_required
def create_supplies():
    form = InventoryForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('lms.supplies'))

    try:
        equipment = Inventory()

        equipment.description = form.description.data
        equipment.maintaining = form.maintaining.data
        equipment.remaining = form.remaining.data
        equipment.type = "supplies"

        equipment.created_by = "{} {}".format(current_user.fname,current_user.lname)

        equipment.save()

        flash('New Supplies Added Successfully!','success')

    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('lms.supplies'))


@bp_lms.route('/supplies/inbound', methods=["POST"])
@login_required
def inbound_supply():
    try:
        supply_id = request.form['supply_id']
        brand = request.form['brand']
        price = decimal.Decimal(request.form['price'])
        quantity = int(request.form['quantity'])

        supply : Inventory = Inventory.objects.get(id=supply_id)

        if supply is None:
            raise Exception("Product cannot be found")

        supply.remaining = supply.remaining + quantity

        supply.transactions.append(
            InboundOutbound(
                brand=brand,
                price=price,
                quantity=quantity,
                total_amount=price * quantity,
                confirm_by=User.objects.get(id=current_user.id)
            )
        )

        supply.save()

        flash('Process Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('lms.supplies'))


@bp_lms.route('/supplies/outbound', methods=["POST"])
@login_required
def outbound_supply():
    # try:
    supply_id = request.form['outbound_supply_id']
    withdraw_by = request.form['withdraw_by']
    date = request.form['date']
    quantity = int(request.form['quantity'])
    remarks = request.form['remarks']
    
    supply : Inventory = Inventory.objects.get(id=supply_id)

    if supply is None:
        raise Exception("Product cannot be found")
    
    supply.remaining = supply.remaining - quantity 
    supply.released = supply.released + quantity if supply.released is not None else quantity

    supply.transactions.append(
        InboundOutbound(
            quantity=quantity,
            date=date,
            remarks=remarks,
            withdraw_by=withdraw_by,
            confirm_by=User.objects.get(id=current_user.id)
        )
    )

    supply.save()

    flash('Process Successfully!','success')
    # except Exception as e:
    #     flash(str(e),'error')
    
    return redirect(url_for('lms.supplies'))


@bp_lms.route('/utilities')
@login_required
def utilities():
    form = InventoryForm()
    form.__heading__ = "Utilities"

    _table_data = []

    _utilities = Inventory.objects(type="utilities")

    for util in _utilities:
        _table_data.append((
            util.id,
            util.maintaining,
            util.description,
            util.released,
            util.remaining,
            util.total_replacement,
        ))

    return admin_table(
        Utilities,
        fields=[],
        form=form,
        table_data=_table_data,
        create_url='lms.create_utilities',
        edit_url='lms.edit_secretary',
        view_modal_url='/learning-management/get-view-utilities-data'
        )


@bp_lms.route('/get-view-utilities-data', methods=['GET'])
@login_required
def get_view_utilities_data():
    _column, _id = request.args.get('column'), request.args.get('id')
    
    try:
        _data = Inventory.objects(id=_id).values_list(_column)

        if _data[0] is None:
            response = jsonify(result='',column=_column)

        else:
            response = jsonify(result=str(_data[0]),column=_column)

        if _column == "branch" and _data[0] is not None:
            response = jsonify(result=str(_data[0].id),column=_column)


    except Exception:
        pass


    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200
    return response


@bp_lms.route('/utilities/create',methods=['GET','POST'])
@login_required
def create_utilities():
    form = InventoryForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('lms.utilities'))

    try:
        _utilities = Inventory()

        _utilities.description = form.description.data
        _utilities.maintaining = form.maintaining.data if form.maintaining.data != '' else None
        _utilities.remaining = form.remaining.data if form.remaining.data != '' else None
        _utilities.price = form.price.data
        _utilities.branch = Branch.objects.get(id=form.branch.data)
        _utilities.type = "utilities"

        _utilities.created_by = "{} {}".format(current_user.fname,current_user.lname)

        _utilities.save()

        flash('New Utility Added Successfully!','success')

    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('lms.utilities'))


@bp_lms.route('/utilities/<string:oid>/edit', methods=['GET', 'POST'])
@login_required
def edit_utilities(oid):
    utility = Inventory.objects.get_or_404(id=oid)
    form = InventoryForm(obj=utility)

    if request.method == "GET":

        return admin_edit(
            Inventory,
            form,
            'lms.edit_utilities',
            oid,
            'lms.utilities',
            )
    
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('lms.utilities'))
        
    try:
        utility.description = form.description.data
        utility.maintaining = form.maintaining.data if form.maintaining.data != '' else None
        utility.remaining = form.remaining.data if form.remaining.data != '' else None
        utility.remaining = form.remaining.data if form.remaining.data != '' else None
        utility.price = form.price.data
        utility.branch = Branch.objects.get(id=form.branch.data)
        utility.type = "utilities"

        utility.set_updated_at()
        utility.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        
        utility.save()
        flash('Utility Updated Successfully!','success')

    except Exception as e:
        flash(str(e),'error')

    return redirect(url_for('lms.utilities'))


# @bp_lms.route('/get-view-secretary-data', methods=['GET'])
# @login_required
# def get_view_user_data():
#     _column, _id = request.args.get('column'), request.args.get('id')

#     _data = User.objects(id=_id).values_list(_column)

#     response = jsonify(result=str(_data[0]),column=_column)

#     if _column == "branch" and _data[0] is not None:
#         response = jsonify(result=str(_data[0].id),column=_column)

#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.status_code = 200
#     return response


# @bp_lms.route('/secretaries/create',methods=['GET','POST'])
# @login_required
# def create_secretary():
#     form = SecretaryForm()

#     if not form.validate_on_submit():
#         for key, value in form.errors.items():
#             flash(str(key) + str(value), 'error')
#         return redirect(url_for('lms.secretaries'))

#     try:
#         secretary = User()

#         secretary.fname = form.fname.data
#         secretary.lname = form.lname.data
#         secretary.branch = Branch.objects.get(id=form.branch.data)
#         secretary.role = Role.objects(name="Secretary").first()
#         secretary.username = form.username.data
#         secretary.email = form.email.data if form.email.data != '' else None
#         secretary.set_password("password")
#         secretary.is_superuser = False

#         secretary.created_by = "{} {}".format(current_user.fname,current_user.lname)

#         secretary.save()

#         flash('New Secretary Added Successfully!','success')

#     except Exception as e:
#         flash(str(e),'error')
    
#     return redirect(url_for('lms.secretaries'))


# @bp_lms.route('/secretaries/<string:oid>/edit', methods=['GET', 'POST'])
# @login_required
# def edit_secretary(oid):
#     secretary = User.objects.get_or_404(id=oid)
#     form = SecretaryEditForm(obj=secretary)

#     if request.method == "GET":

#         return admin_edit(
#             Secretary,
#             form,
#             'lms.edit_secretary',
#             oid,
#             'lms.secretaries',
#             )
    
#     if not form.validate_on_submit():
#         for key, value in form.errors.items():
#             flash(str(key) + str(value), 'error')
#         return redirect(url_for('lms.secretaries'))
        
#     try:
#         secretary.fname = form.fname.data
#         secretary.lname = form.lname.data
#         secretary.branch = Branch.objects.get(id=form.branch.data)
#         secretary.role = Role.objects(name="Secretary").first()
#         secretary.username = form.username.data
#         secretary.email = form.email.data if form.email.data != '' else None
#         secretary.updated_at = datetime.now(TIMEZONE)
#         secretary.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        
#         secretary.save()
#         flash('Secretary Updated Successfully!','success')

#     except Exception as e:
#         flash(str(e),'error')

#     return redirect(url_for('lms.secretaries'))
