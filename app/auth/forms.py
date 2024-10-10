from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from app.admin.forms import AdminTableForm, AdminEditForm, AdminInlineForm, AdminField
from .models import Role



class UserForm(AdminTableForm):
    __heading__ = "Users"
    __table_columns__ = ['Username', 'First name', 'last name', 'role', 'email']

    username = AdminField(label='Username', validators=[DataRequired()])
    email = AdminField(label='Email', type='email',required=False)
    fname = AdminField(label='First Name', validators=[DataRequired()])
    lname = AdminField(label='Last Name', validators=[DataRequired()])
    role = AdminField(label='Role',validators=[DataRequired()],type='number',model=Role)

    @property
    def fields(self):
        return [[self.fname, self.lname],[self.username,self.email],[self.role]]


class PermissionInlineForm(AdminInlineForm):
    __table_id__ = 'tbl_inline_permissions'
    __table_columns__ =['Model','Read','create','write','delete']
    __title__ = "Permissions"
    __html__ = 'auth/permission_inline.html'


class UserEditForm(AdminEditForm):
    __heading__ = "Edit User"

    username = AdminField(label='Username', validators=[DataRequired()])
    email = AdminField(label='Email', type='email',required=False)
    fname = AdminField(label='First Name', validators=[DataRequired()])
    lname = AdminField(label='Last Name', validators=[DataRequired()])
    is_employee = AdminField(label="Is Employee?", type='checkbox')
    is_teacher = AdminField(label="Is Teacher?", type='checkbox')

    @property
    def fields(self):
        return [[self.fname, self.lname],[self.username,self.email], [self.is_employee], [self.is_teacher]]

    # @property
    # def inlines(self):
    #     return [self.permission_inline]


class UserPermissionForm(AdminTableForm):
    index_headers = ['Username', 'Name', 'Model', 'Read','create', 'Write', 'Delete']
    index_title = "User Permissions"
    index_message = "Message"


class RoleModelInlineForm(AdminInlineForm):
    __table_id__ = 'tbl_inline_permissions'
    __table_columns__ = ['Model','Read','create','write','delete']
    __title__ = "Add role permissions"


class RoleCreateForm(AdminTableForm):
    __heading__ = "User Roles"
    __table_columns__ = ['Name', 'created at', 'updated at']
    __subheading__ = "Groups of permissions"

    name = AdminField(label="Name",validators=[DataRequired()])

    inline = RoleModelInlineForm()

    @property
    def fields(self):
        return [[self.name]]

    @property
    def inlines(self):
        return [self.inline]


class RoleEditForm(AdminEditForm):
    __heading__ = "Edit Role"

    name = AdminField(label="Name",validators=[DataRequired()])

    permission_inline = PermissionInlineForm()
    permission_inline.__html__ = "auth/role_permission_inline.html"

    @property
    def fields(self):
        return [[self.name]]

    @property
    def inlines(self):
        return [self.permission_inline]


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log in')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    branch = StringField('Branch', validators=[DataRequired()])
    position = StringField('position', validators=[DataRequired()])
    fname = StringField('Fname', validators=[DataRequired()])
    lname = StringField('Lname', validators=[DataRequired()])
    suffix = StringField('Suffix')
    nickname = StringField('Nickname', validators=[DataRequired()])
    date_of_birth = StringField('Date of Birth', validators=[DataRequired()])
    contact_no = StringField('Contact No.', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired()])
    father_name = StringField('Fathers Name', validators=[DataRequired()])
    mother_name = StringField('Mothers Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log in')

class SendUsAMessageForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    subscribe = StringField('Subscribe')
    submit = SubmitField('Submit')