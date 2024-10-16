from bson import ObjectId
from flask import request, redirect, url_for, flash, jsonify
from app.admin.templating import admin_render_template
from app import mongo
from prime_admin import bp_lms
from prime_admin.models import Settings, Branch
from prime_admin.forms import BranchForm


@bp_lms.route('/settings')
def settings():
    return admin_render_template(
        Settings, "lms/settings_page.html", 'learning_management'
        )
    
    
@bp_lms.route('/settings/other-expenses')
def other_expenses_settings():
    return admin_render_template(
        Settings, 'lms/settings/other_expenses_settings_page.html', 'learning_management'
    )
    

@bp_lms.route('/settings/examination/batch-numbers')
def batch_numbers_settings():
    return admin_render_template(
        Settings, 'lms/settings/examination/batch_numbers_settings_page.html', 'learning_management'
    )


@bp_lms.route('/settings/examination/sessions')
def sessions_settings():
    return admin_render_template(
        Settings, 'lms/settings/examination/sessions_settings_page.html', 'learning_management'
    )


@bp_lms.route('/settings/examination/venues')
def venues_settings():
    return admin_render_template(
        Settings, 'lms/settings/examination/venues_settings_page.html', 'learning_management'
    )


@bp_lms.route('/settings/examination/industries')
def industries_settings():
    return admin_render_template(
        Settings, 'lms/settings/examination/industries_settings_page.html', 'learning_management'
    )


@bp_lms.route('/settings/orientators')
def orientators_settings():
    return admin_render_template(
        Settings, 'lms/settings/orientators_settings_page.html', 'learning_management'
    )


@bp_lms.route('/settings/examination/klts')
def klts_settings():
    return admin_render_template(
        Settings, 'lms/settings/examination/no_of_klt_settings_page.html', 'learning_management'
    )


# @bp_lms.route('/settings/branches')
# def branch_settings():
#     form = BranchForm()

#     _table_data = []

#     for branch in Branch.objects:
#         _table_data.append((
#             branch.id,
#             branch.name,
#             branch.created_by,
#             branch.created_at_local,
#             branch.updated_by,
#             branch.updated_at_local,
#         ))
        
#     TABLE_OPTIONS = {
        
#     }
#     return admin_render_template(
#         Settings, 'lms/settings/branch_settings_page.html', 'learning_management',
#         form=form,
#         table_data=_table_data,
#         create_url='lms.create_branch',
#         edit_url='lms.edit_branch',
#         view_modal_url='/learning-management/get-view-branch-data',
#         TABLE_OPTIONS=TABLE_OPTIONS
#     )


@bp_lms.route('/settings/other-expenses/create', methods=['POST'])
def create_other_expenses():
    description = request.form['description']
    
    if description == "":
        return redirect(url_for('lms.other_expenses_settings'))

    mongo.db.lms_other_expenses_items.insert_one({
        'description': description.upper()
    })
    flash("Added successfully!", 'success')
    return redirect(url_for('lms.other_expenses_settings'))


@bp_lms.route('/settings/examination/batch-numbers/create', methods=['POST'])
def create_batch_number():
    description = request.form['description']
    
    if description == "":
        return redirect(url_for('lms.batch_numbers_settings'))

    mongo.db.lms_examination_batch_numbers.insert_one({
        'description': description
    })
    flash("Added successfully!", 'success')
    return redirect(url_for('lms.batch_numbers_settings'))


@bp_lms.route('/settings/examination/session/create', methods=['POST'])
def create_session():
    description = request.form['description']
    
    if description == "":
        return redirect(url_for('lms.sessions_settings'))

    mongo.db.lms_examination_sessions.insert_one({
        'description': description
    })
    flash("Added successfully!", 'success')
    return redirect(url_for('lms.sessions_settings'))
    
    

@bp_lms.route('/settings/examination/industries/create', methods=['POST'])
def create_industry():
    description = request.form['description']
    
    if description == "":
        return redirect(url_for('lms.industries_settings'))

    mongo.db.lms_configurations.update_one({
        'name': "industries"
    }, {"$push": {
        'values': description
    }})
    flash("Added successfully!", 'success')
    return redirect(url_for('lms.industries_settings'))


@bp_lms.route('/settings/examination/venues/create', methods=['POST'])
def create_venue():
    description = request.form['description']
    
    if description == "":
        return redirect(url_for('lms.venues_settings'))

    mongo.db.lms_configurations.update_one({
        'name': "exam_venues"
    }, {"$push": {
        'values': description
    }})
    flash("Added successfully!", 'success')
    return redirect(url_for('lms.venues_settings'))


@bp_lms.route('/settings/orientators/create', methods=['POST'])
def create_orientator():
    name = request.form['name']
    
    if name == "":
        return redirect(url_for('lms.orientators_settings'))

    mongo.db.lms_orientators.insert_one({
        'fname': name
    })
    flash("Added successfully!", 'success')
    return redirect(url_for('lms.orientators_settings'))


@bp_lms.route('/settings/examination/klts/create', methods=['POST'])
def create_klt():
    description = request.form['description']
    
    if description == "":
        return redirect(url_for('lms.klts_settings'))

    mongo.db.lms_klts.insert_one({
        'description': description
    })
    flash("Added successfully!", 'success')
    return redirect(url_for('lms.klts_settings'))
    

@bp_lms.route('/settings/orientators/toggle-status', methods=['POST'])
def toggle_orientators_status():
    orientator_id = request.json['orientator']

    mongo.db.lms_orientators.update_one({
        '_id': ObjectId(orientator_id)
    }, [{'$set': {
        "is_active": {
            "$eq": [False,"$is_active"]
        }}}])
    return jsonify({'result': True})
